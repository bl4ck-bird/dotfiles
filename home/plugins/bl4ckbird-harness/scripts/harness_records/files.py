"""기록 루트 내부의 링크를 따라가지 않는 읽기와 원자적 게시."""

from contextlib import contextmanager
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import uuid

from .errors import RecordError

MAX_BYTES = 32 * 1024 * 1024


def digest(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False) + "\n").encode()


def decode_json(data):
    def unique(items):
        result = {}
        for key, value in items:
            if key in result:
                raise RecordError("Duplicate JSON key: " + key)
            result[key] = value
        return result
    try:
        return json.loads(data, object_pairs_hook=unique,
                          parse_constant=lambda value: (_ for _ in ()).throw(RecordError("Invalid JSON number")))
    except (ValueError, UnicodeError) as error:
        raise RecordError("Invalid JSON: " + str(error)) from error


def relative(value):
    if not isinstance(value, str) or not value or "\\" in value or "\x00" in value:
        raise RecordError("Invalid relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in ("", ".", "..") for part in value.split("/")):
        raise RecordError("Path must remain inside the record root")
    return path.parts


class Files:
    def __init__(self, root):
        requested = Path(root).absolute()
        if requested.is_symlink() or requested.name != ".harness":
            raise RecordError("An explicit, non-symlink .harness directory is required")
        requested.mkdir(parents=True, exist_ok=True)
        self.root = requested.resolve()

    @contextmanager
    def parent(self, name, create=False):
        parts = relative(name)
        fd = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            for part in parts[:-1]:
                if create:
                    try:
                        os.mkdir(part, 0o700, dir_fd=fd)
                    except FileExistsError:
                        pass
                next_fd = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
                os.close(fd)
                fd = next_fd
            yield fd, parts[-1]
        except OSError as error:
            raise RecordError("Unsafe or unavailable path: " + name + " (" + type(error).__name__ + ")") from error
        finally:
            os.close(fd)

    def read(self, name):
        with self.parent(name) as (fd, leaf):
            file_fd = os.open(leaf, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
            with os.fdopen(file_fd, "rb") as stream:
                if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                    raise RecordError("Expected a regular evidence file: " + name)
                data = stream.read(MAX_BYTES + 1)
                if len(data) > MAX_BYTES:
                    raise RecordError("Evidence file exceeds supported 32 MiB: " + name)
                return data

    def exists(self, name):
        try:
            with self.parent(name) as (fd, leaf):
                info = os.stat(leaf, dir_fd=fd, follow_symlinks=False)
                if not stat.S_ISREG(info.st_mode):
                    raise RecordError("Expected a regular file: " + name)
                return True
        except RecordError as error:
            if isinstance(error.__cause__, FileNotFoundError):
                return False
            raise

    def publish(self, name, data, replace=False, expected_digest=None):
        if len(data) > MAX_BYTES:
            raise RecordError("Evidence file exceeds supported 32 MiB")
        with self.parent(name, create=True) as (fd, leaf):
            temporary = ".pending-" + uuid.uuid4().hex
            temp_fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=fd)
            try:
                with os.fdopen(temp_fd, "wb") as stream:
                    stream.write(data)
                    stream.flush()
                    os.fsync(stream.fileno())
                if replace:
                    if expected_digest is not None and digest(self.read(name)) != expected_digest:
                        raise RecordError("Target changed before publication: " + name)
                    os.replace(temporary, leaf, src_dir_fd=fd, dst_dir_fd=fd)
                else:
                    os.link(temporary, leaf, src_dir_fd=fd, dst_dir_fd=fd, follow_symlinks=False)
                os.fsync(fd)
            finally:
                try:
                    os.unlink(temporary, dir_fd=fd)
                except FileNotFoundError:
                    pass
        return {"path": name, "sha256": digest(data)}

    def reference(self, name):
        return {"path": name, "sha256": digest(self.read(name))}

    def entries(self, prefix):
        try:
            with self.parent(prefix + "/.probe") as (fd, _):
                names = os.listdir(fd)
                for name in names:
                    if stat.S_ISLNK(os.stat(name, dir_fd=fd, follow_symlinks=False).st_mode):
                        raise RecordError("Symlink in record inventory: " + prefix + "/" + name)
                return sorted(names)
        except RecordError as error:
            if isinstance(error.__cause__, FileNotFoundError):
                return []
            raise

    def scan(self, prefix):
        parts = relative(prefix)
        base = self.root.joinpath(*parts)
        if not self.entries(prefix):
            return []
        result = []
        for parent, dirs, names in os.walk(base, followlinks=False):
            for name in dirs + names:
                path = Path(parent) / name
                if path.is_symlink():
                    raise RecordError("Symlink in record inventory: " + str(path.relative_to(self.root)))
            result.extend(str((Path(parent) / name).relative_to(self.root)) for name in names if not name.startswith(".pending-"))
        return sorted(result)

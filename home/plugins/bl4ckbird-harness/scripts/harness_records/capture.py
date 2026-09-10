"""명시한 문서와 코드만 캡처하고 작업 트리와 index를 구분한다."""

import os
from pathlib import Path
import stat
import subprocess

from .errors import RecordError
from .files import MAX_BYTES, digest, relative
from .identifiers import require_reservation
from .store import stamp


def reject_secret_candidates(parts, path):
    for part in parts:
        lower = part.lower()
        if (lower == ".env" or lower.startswith(".env.") or lower in {"id_rsa", "id_ed25519", "credentials", "credentials.json", "auth.json"}
                or lower.endswith((".pem", ".key", ".p12", ".pfx"))):
            raise RecordError("Secret-candidate input is not captured: " + str(path))


def safe_name(path):
    parts = relative(path)
    reject_secret_candidates(parts, path)
    return parts


def safe_source_path(path):
    candidate = Path(path)
    parts = candidate.parts[1:] if candidate.is_absolute() else candidate.parts
    reject_secret_candidates(parts, candidate)


def git(workspace, *args, optional=False):
    environment = os.environ.copy()
    environment["GIT_NO_LAZY_FETCH"] = "1"
    try:
        result = subprocess.run(["git", "--no-optional-locks", "--literal-pathspecs", "-c", "core.fsmonitor=false",
                                 "-C", str(workspace), *args], capture_output=True, timeout=30, env=environment)
    except subprocess.TimeoutExpired as error:
        raise RecordError("Git capture did not finish within 30 seconds") from error
    if result.returncode and not optional:
        raise RecordError("Git capture failed: " + args[0])
    return result.stdout if result.returncode == 0 else None


def source_file(root, path):
    parts = safe_name(path)
    fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        for component in parts[:-1]:
            next_fd = os.open(component, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        try:
            info = os.stat(parts[-1], dir_fd=fd, follow_symlinks=False)
        except FileNotFoundError:
            return {"kind": "deleted", "mode": None, "data": None, "link_target": None}
        if stat.S_ISLNK(info.st_mode):
            target = os.readlink(parts[-1], dir_fd=fd)
            return {"kind": "symlink", "mode": stat.S_IMODE(info.st_mode), "data": target.encode(), "link_target": target}
        if not stat.S_ISREG(info.st_mode):
            raise RecordError("Capture requires explicit files, not directories/devices: " + path)
        source_fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
        with os.fdopen(source_fd, "rb") as stream:
            current = os.fstat(stream.fileno())
            if not stat.S_ISREG(current.st_mode):
                raise RecordError("Input changed file type during capture")
            data = stream.read(MAX_BYTES + 1)
            after = os.fstat(stream.fileno())
            if len(data) > MAX_BYTES or (current.st_ino, current.st_size, current.st_mtime_ns) != (after.st_ino, after.st_size, after.st_mtime_ns):
                raise RecordError("Input exceeded size support or changed during capture")
        return {"kind": "file", "mode": stat.S_IMODE(current.st_mode), "data": data, "link_target": None}
    except FileNotFoundError:
        return {"kind": "deleted", "mode": None, "data": None, "link_target": None}
    except OSError as error:
        raise RecordError("Unsafe or unreadable capture input: " + path) from error
    finally:
        os.close(fd)


def save_content(store, prefix, data):
    if data is None:
        return None
    path = prefix + "/contents/" + digest(data)
    if store.files.exists(path):
        if store.files.read(path) != data:
            raise RecordError("Existing preserved content does not match its hash")
        return store.files.reference(path)
    return store.files.publish(path, data)


def capture_documents(store, work_id, record_id, documents):
    require_reservation(store.files, "bundle", record_id, work_id)
    prefix = "work/" + work_id + "/snapshots/" + record_id
    record = {**stamp("bundle", record_id, work_id), "documents": []}
    if not documents or len({item["path"] for item in documents}) != len(documents):
        raise RecordError("A unique explicit document list is required")
    originals = {}
    for item in documents:
        safe_name(item["path"])
        data = store.files.read(item["path"])
        originals[item["path"]] = data
        record["documents"].append({"source_path": item["path"], "copy_ref": save_content(store, prefix, data), "role": item["role"]})
    for path, data in originals.items():
        if store.files.read(path) != data:
            raise RecordError("Document changed during bundle capture")
    return store.publish(record)


def code_observation(workspace, path, has_git):
    source = source_file(workspace, path)
    index_data = index_mode = None
    status = "no_repository"
    if has_git:
        entries = git(workspace, "ls-files", "--stage", "-z", "--", path).split(b"\0")
        entries = [item for item in entries if item]
        if len(entries) > 1:
            raise RecordError("Unmerged index requires reconciliation before capture")
        if entries:
            metadata, actual_path = entries[0].split(b"\t", 1)
            if actual_path != os.fsencode(path):
                raise RecordError("Git returned a different path from the explicit capture input")
            mode, object_id, stage = metadata.decode().split()
            if stage != "0" or mode == "160000":
                raise RecordError("Unmerged index/submodule requires explicit external-input evidence")
            index_mode = mode
            index_data = git(workspace, "cat-file", "blob", object_id)
            if len(index_data) > MAX_BYTES:
                raise RecordError("Index content exceeds supported size")
        status_bytes = git(workspace, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--ignored=matching", "--", path)
        status = status_bytes[:2].decode() if status_bytes else "clean"
    return {**source, "index_data": index_data, "index_mode": index_mode, "git_status": status}


def capture_code(store, work_id, record_id, workspace, workspace_id, paths, scope,
                 base_commit=None, exclusions=None, external_inputs=None):
    require_reservation(store.files, "code_target", record_id, work_id)
    requested = Path(workspace).absolute()
    if requested.is_symlink() or not requested.is_dir():
        raise RecordError("Explicit regular code workspace is required")
    workspace = requested.resolve()
    if not paths or len(set(paths)) != len(paths):
        raise RecordError("A unique explicit code-file list is required")
    for path in paths:
        safe_name(path)
    has_git = git(workspace, "rev-parse", "--is-inside-work-tree", optional=True) == b"true\n"
    head_bytes = git(workspace, "rev-parse", "--verify", "HEAD", optional=True) if has_git else None
    head = head_bytes.decode().strip() if head_bytes else None
    if base_commit is not None:
        import re
        if not has_git or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", base_commit):
            raise RecordError("Base commit must be an available full object ID or null")
        git(workspace, "cat-file", "-e", base_commit + "^{commit}")
    record = {**stamp("code_target", record_id, work_id), "workspace_id": workspace_id,
              "workspace": str(workspace), "base_commit": base_commit, "head": head, "scope": scope,
              "inclusions": paths, "exclusions": exclusions or [], "files": [], "external_inputs": external_inputs or [],
              "limitations": ["Only explicitly selected inputs are captured; scope completeness is a main-agent judgment",
                              "Matching observations do not exclude transient concurrent changes",
                              "No secret candidate contents or environment dump are captured"]}
    prefix = "work/" + work_id + "/snapshots/code/" + record_id
    observations = {}
    for path in paths:
        item = code_observation(workspace, path, has_git)
        observations[path] = item
        record["files"].append({"path": path, "kind": item["kind"], "mode": item["mode"],
                                "sha256": digest(item["data"]) if item["data"] is not None else None,
                                "content_ref": save_content(store, prefix, item["data"]), "link_target": item["link_target"],
                                "git_status": item["git_status"], "index_mode": item["index_mode"],
                                "index_sha256": digest(item["index_data"]) if item["index_data"] is not None else None,
                                "index_content_ref": save_content(store, prefix, item["index_data"])})
    if any(code_observation(workspace, path, has_git) != item for path, item in observations.items()):
        raise RecordError("Code or index changed during capture")
    if has_git and git(workspace, "rev-parse", "--verify", "HEAD", optional=True) != head_bytes:
        raise RecordError("HEAD changed during capture")
    return store.publish(record)


def compare_target(store, reference):
    record = store.read_record(reference["path"])
    kind = record["kind"]
    if kind not in {"bundle", "code_target"}:
        raise RecordError("Expected a document/code target")
    store.read_ref(reference, kind)
    changes = []
    if kind == "bundle":
        for document in record["documents"]:
            try:
                current = store.files.reference(document["source_path"])["sha256"]
            except RecordError:
                current = None
            if current != document["copy_ref"]["sha256"]:
                changes.append(document["source_path"])
    else:
        workspace = Path(record["workspace"])
        has_git = git(workspace, "rev-parse", "--is-inside-work-tree", optional=True) == b"true\n"
        current_head = git(workspace, "rev-parse", "--verify", "HEAD", optional=True) if has_git else None
        if (current_head.decode().strip() if current_head else None) != record["head"]:
            changes.append("HEAD")
        for old in record["files"]:
            current = code_observation(workspace, old["path"], has_git)
            value = {"kind": current["kind"], "mode": current["mode"], "git_status": current["git_status"],
                     "sha256": digest(current["data"]) if current["data"] is not None else None,
                     "index_mode": current["index_mode"],
                     "index_sha256": digest(current["index_data"]) if current["index_data"] is not None else None}
            if any(old[key] != item for key, item in value.items()):
                changes.append(old["path"])
    return {"matches": not changes, "changed_inputs": changes, "preserved_target_intact": True,
            "limitations": ["Environment applicability and transient changes require separate judgment"]}


def same_code_target(first, second):
    def identity(record):
        files = [{key: value for key, value in item.items() if key not in {"content_ref", "index_content_ref"}}
                 for item in record["files"]]
        return {"workspace_id": record["workspace_id"], "workspace": record["workspace"], "head": record["head"],
                "files": sorted(files, key=lambda item: item["path"]), "external_inputs": record["external_inputs"],
                "inclusions": sorted(record["inclusions"]), "exclusions": sorted(record["exclusions"])}
    return identity(first) == identity(second)

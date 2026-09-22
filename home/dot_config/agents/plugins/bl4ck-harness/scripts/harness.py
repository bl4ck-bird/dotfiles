#!/usr/bin/env python3
"""프로젝트 기록의 초기화·상태 모순과 참조 확인·대상 보존을 수행한다."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from urllib.parse import unquote, urlsplit
import uuid

from status import has_status_fields, prose_lines, validate_status


class RecordError(Exception):
    pass


CONFIG = {"plugin": "bl4ck-harness", "schema_version": 1, "enabled": True}


def contained(base, path):
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


def safe_path(base, path):
    """기록 경로를 통해 프로젝트 밖 파일을 읽거나 바꾸지 않는다."""
    absolute = path.absolute()
    if not contained(base, absolute):
        raise RecordError("프로젝트 밖 경로는 사용할 수 없습니다.")
    cursor = base
    for part in absolute.relative_to(base).parts:
        if part == '..':
            raise RecordError("상위 경로 이동은 사용할 수 없습니다.")
        cursor = cursor / part
        if cursor.is_symlink():
            raise RecordError("심볼릭 링크 경로는 사용할 수 없습니다: " + str(cursor))
    if not contained(base, absolute.resolve()):
        raise RecordError("프로젝트 밖 경로는 사용할 수 없습니다.")
    return absolute


def project_root(value):
    root = Path(value).expanduser().resolve()
    if not root.is_dir():
        raise RecordError("프로젝트 디렉터리가 없습니다: " + str(root))
    try:
        result = subprocess.run(
            ['git', '-C', str(root), 'rev-parse', '--show-toplevel'],
            capture_output=True, text=True, check=False)
    except FileNotFoundError:
        return root
    if result.returncode == 0 and Path(result.stdout.strip()).resolve() != root:
        raise RecordError("Git 저장소의 최상위 경로를 지정하세요.")
    return root


def tracked_records(root):
    try:
        result = subprocess.run(
            ['git', '-C', str(root), 'ls-files', '-z', '--', '.harness'],
            capture_output=True, check=False)
    except FileNotFoundError:
        return False
    return result.returncode == 0 and bool(result.stdout)


def config_path(root):
    return safe_path(root, root / '.harness' / 'config.json')


def read_config(root):
    path = config_path(root)
    try:
        value = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise RecordError("설정을 읽을 수 없습니다: " + str(exc))
    if (not isinstance(value, dict) or set(value) != set(CONFIG)
            or value.get('plugin') != 'bl4ck-harness'
            or type(value.get('schema_version')) is not int
            or value['schema_version'] != 1
            or type(value.get('enabled')) is not bool):
        raise RecordError("지원하지 않는 설정입니다. 기존 설정을 자동 변환하지 않습니다.")
    if not value['enabled']:
        raise RecordError("비활성 설정입니다. 명시적으로 활성화한 뒤 다시 실행하세요.")
    return value


def write_new(path, content):
    with path.open('x', encoding='utf-8') as handle:
        handle.write(content)


def effective_record_ignore(root):
    """Git 저장소에서는 뒤따르는 예외 규칙까지 반영한 결과를 확인한다."""
    try:
        repository = subprocess.run(
            ['git', '-C', str(root), 'rev-parse', '--is-inside-work-tree'],
            capture_output=True, text=True, check=False)
        if repository.returncode != 0:
            return True
        result = subprocess.run(
            ['git', '-C', str(root), 'check-ignore', '--quiet', '--no-index', '--', '.harness/'],
            capture_output=True, check=False)
    except FileNotFoundError:
        return True
    return result.returncode == 0


def initialize(root):
    records = safe_path(root, root / '.harness')
    ignore = safe_path(root, root / '.gitignore')
    path = config_path(root)
    if tracked_records(root):
        raise RecordError("이미 추적 중인 하네스 기록이 있습니다. 이관 범위를 먼저 확인하세요.")
    if (records / 'config.toml').exists():
        raise RecordError("다른 하네스 설정이 있습니다. 자동 이관하지 않습니다.")
    if path.exists():
        read_config(root)
    elif records.exists() and any(records.iterdir()):
        raise RecordError("기존 기록이 있습니다. 소유·이관 범위를 먼저 확인하세요.")
    current = safe_path(root, records / 'CURRENT.md')
    original = ignore.read_text(encoding='utf-8') if ignore.exists() else ''
    # 기록을 쓰기 전에 제외 규칙을 준비한다. 이 작업은 다중 파일 트랜잭션이 아니다.
    if '/.harness/' not in original.splitlines() or not effective_record_ignore(root):
        with ignore.open('a', encoding='utf-8') as handle:
            handle.write(('\n' if original and not original.endswith('\n') else '') + '/.harness/\n')
    if not effective_record_ignore(root):
        raise RecordError("Git 제외가 적용되지 않았습니다. 기록 작성 전에 제외 설정을 확인하세요.")
    records.mkdir(exist_ok=True)
    if not path.exists():
        write_new(path, json.dumps(CONFIG, ensure_ascii=False, indent=2) + '\n')
    if not current.exists():
        write_new(current, '# 현재 상태\n\nbl4ck-harness이 활성화되었습니다. 아직 진행 중인 변경은 없습니다.\n\n## 다음 행동\n\n사용자 요청과 기존 근거를 확인해 필요한 단계에서 시작합니다.\n')
    print("프로젝트 기록 준비 완료: " + str(records))


LINK = re.compile(r'(?<!!)\[[^\]\n]+\]\((<[^>]+>|[^)\s]+)(?:\s+"[^"\n]*")?\)')


def local_links(text):
    # 코드 예시는 실제 문서 참조가 아니므로 검사에서 제외한다.
    for match in LINK.finditer('\n'.join(prose_lines(text))):
        destination = match.group(1).strip('<>')
        parsed = urlsplit(destination)
        if parsed.scheme or not parsed.path:
            continue
        yield unquote(parsed.path)


def check_record_boundary(root):
    read_config(root)
    if tracked_records(root):
        raise RecordError("Git이 하네스 기록을 추적하고 있습니다.")
    ignore = safe_path(root, root / '.gitignore')
    if not ignore.is_file() or '/.harness/' not in ignore.read_text(encoding='utf-8').splitlines():
        raise RecordError("루트 .gitignore에 /.harness/ 규칙이 없습니다.")
    if not effective_record_ignore(root):
        raise RecordError("Git이 .harness/를 실제로 제외하지 않습니다. 예외 규칙을 확인하세요.")


def check(root):
    check_record_boundary(root)
    records = root / '.harness'
    current = safe_path(root, records / 'CURRENT.md')
    if not current.is_file():
        raise RecordError("CURRENT.md가 없습니다.")
    current_targets = {(current.parent / link).resolve()
                       for link in local_links(current.read_text(encoding='utf-8'))}
    count = 0
    legacy_count = 0
    for path in records.rglob('*'):
        safe_path(root, path)
        if not path.is_file() or path.suffix != '.md' or 'snapshots' in path.relative_to(records).parts:
            continue
        count += 1
        content = path.read_text(encoding='utf-8')
        relative = path.relative_to(records)
        if len(relative.parts) == 3 and relative.parts[0] == 'changes' and path.name == 'status.md':
            if path.resolve() in current_targets or has_status_fields(content):
                try:
                    state = validate_status(content)
                except ValueError as exc:
                    raise RecordError(str(relative) + ': ' + str(exc))
                if state != '완료' and path.resolve() not in current_targets:
                    raise RecordError('CURRENT.md에 활성 변경의 status.md 링크가 없습니다. 인라인 형식으로 연결하세요: [변경](' + relative.as_posix() + ')')
            else:
                legacy_count += 1
        for target in local_links(content):
            joined = path.parent / target
            # 정상적인 상대 참조는 정규화하되 링크를 통과하는 원래 경로도 확인한다.
            if any(parent.is_symlink() for parent in [joined, *joined.parents] if contained(root, parent)):
                raise RecordError("참조에 심볼릭 링크가 있습니다: " + str(path))
            resolved = joined.resolve()
            if not contained(root, resolved) or not resolved.exists():
                raise RecordError("확인할 수 없는 문서 참조: " + str(path) + ' -> ' + target)
    print("구조·참조·상태 모순 검사 통과: 문서 " + str(count) + "개. 실제 실행·승인·검증의 의미는 별도 확인이 필요합니다.")
    if legacy_count:
        print('상태 형식 미검사: CURRENT에 연결되지 않은 이전 자유형식 상태 ' + str(legacy_count) + '개. 해당 기록의 활성 여부는 판정하지 않았습니다.')


def snapshot(root, change, files):
    check_record_boundary(root)
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', change):
        raise RecordError("변경명은 소문자·숫자와 단일 하이픈으로 작성하세요.")
    records = root / '.harness'
    change_dir = safe_path(root, records / 'changes' / change)
    if not change_dir.is_dir():
        raise RecordError("변경 디렉터리를 먼저 작성하세요.")
    sources = []
    for value in files:
        relative = Path(value)
        source = safe_path(records, records / relative)
        if relative.is_absolute() or not source.is_file() or source.suffix != '.md':
            raise RecordError("기존 기록 Markdown 파일만 보존할 수 있습니다: " + value)
        if 'snapshots' in relative.parts:
            raise RecordError("스냅샷을 다시 스냅샷에 포함할 수 없습니다.")
        if relative in [item[0] for item in sources]:
            raise RecordError("같은 파일을 중복 지정했습니다.")
        sources.append((relative, source.read_bytes()))
    destination = safe_path(root, change_dir / 'snapshots' / ('snapshot-' + uuid.uuid4().hex))
    destination.mkdir(parents=True, exist_ok=False)
    manifest = {'created_at': datetime.now(timezone.utc).isoformat(), 'files': []}
    try:
        for relative, data in sources:
            copied = destination / 'files' / relative
            copied.parent.mkdir(parents=True, exist_ok=True)
            copied.write_bytes(data)
            manifest['files'].append({'path': str(relative), 'sha256': hashlib.sha256(data).hexdigest()})
        write_new(destination / 'manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    except OSError:
        # 이번 호출이 만든 불완전한 사본만 정리하고 원본은 보존한다.
        shutil.rmtree(destination)
        raise
    print("대상 보존 완료: " + str(destination))


def main():
    parser = argparse.ArgumentParser(description='하네스 기록 초기화·구조와 상태 확인·대상 보존')
    commands = parser.add_subparsers(dest='command', required=True)
    for name, help_text in [('init', '명시적으로 프로젝트 적용'), ('check', '설정·참조·상태 모순 확인'), ('snapshot', '승인·리뷰 대상 보존')]:
        command = commands.add_parser(name, help=help_text)
        command.add_argument('--root', required=True, help='프로젝트 최상위 경로')
        if name == 'snapshot':
            command.add_argument('--change', required=True, help='변경명')
            command.add_argument('--files', nargs='+', required=True, help='.harness 기준 Markdown 경로')
    args = parser.parse_args()
    try:
        root = project_root(args.root)
        if args.command == 'init':
            initialize(root)
        elif args.command == 'check':
            check(root)
        else:
            snapshot(root, args.change, args.files)
    except (RecordError, OSError) as exc:
        print("실행 보류: " + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())

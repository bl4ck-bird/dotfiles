"""기계적 기록 작업만 제공하는 명령행 인터페이스."""

import argparse
import json
from pathlib import Path
import sys

from .capture import capture_code, capture_documents, compare_target, safe_source_path, source_file
from .errors import RecordError
from .files import decode_json, relative
from .identifiers import KINDS, reserve
from .recovery import reconcile
from .schema import FIELDS, ID, schema, template, validate
from .state import update_current, update_state
from .repair import repair_state
from .store import Store


def payload(path):
    return decode_json(Path(path).read_bytes())


def parser():
    root = argparse.ArgumentParser(description="불변 근거 게시·명시 대상 캡처·단일 작업 상태 검사. 호스트 호출은 실행하지 않습니다.")
    root.add_argument("--root", type=Path, help="명시적인 프로젝트 .harness 경로")
    commands = root.add_subparsers(dest="command", required=True)
    for name in ("schema", "template"):
        command = commands.add_parser(name, help="정확한 형식 / 작성할 입력의 빈 구조 조회")
        command.add_argument("kind", choices=sorted(FIELDS) + ["state"])
    command = commands.add_parser("reserve", help="종류·부모 범위에 영구 ID 예약")
    command.add_argument("--kind", choices=sorted(KINDS), required=True)
    command.add_argument("--name", required=True)
    command.add_argument("--timezone", required=True)
    command.add_argument("--work-id")
    command = commands.add_parser("reference", help="기존 근거의 경로·해시 참조 생성")
    command.add_argument("--path", required=True)
    command = commands.add_parser("put-evidence", help="명시한 비밀정보 제거 자료를 새 근거로 보존")
    command.add_argument("--source", type=Path, required=True)
    command.add_argument("--path", required=True)
    command = commands.add_parser("publish", help="종류별 정확 필드·기존 참조 확인 후 새 불변 기록 게시")
    command.add_argument("--input", required=True)
    command = commands.add_parser("state-update", help="메인이 판단한 상태를 예상 revision으로 게시")
    command.add_argument("--input", required=True)
    command.add_argument("--expected-revision", type=int, required=True)
    command = commands.add_parser("state-repair", help="원본·재구성 상태·수리 판단을 보존한 뒤 명시적으로 상태 교체")
    command.add_argument("--input", required=True)
    command.add_argument("--record-id", required=True)
    command.add_argument("--expected-sha256", required=True)
    command.add_argument("--reason", required=True)
    command.add_argument("--evidence", required=True, help="판단 근거 path/sha256 목록 JSON 파일")
    command = commands.add_parser("update-current", help="명시한 파생 안내만 갱신; 실행을 재시도하지 않음")
    command.add_argument("--input", required=True)
    command.add_argument("--expected-sha256")
    command = commands.add_parser("reconcile", help="원기록에서 불확실 실행·누락 근거·시도 사용량 보고")
    command.add_argument("--work-id", required=True)
    command = commands.add_parser("capture-docs", help="검토할 명시 문서 목록을 불변 묶음으로 캡처")
    command.add_argument("--work-id", required=True)
    command.add_argument("--record-id", required=True)
    command.add_argument("--documents", required=True, help='[{"path":"work/.../spec.md","role":"target"}] JSON 파일')
    command = commands.add_parser("capture-code", help="명시 코드 파일과 index를 별도 보존")
    for name in ("work-id", "record-id", "workspace", "workspace-id", "scope"):
        command.add_argument("--" + name, required=True)
    command.add_argument("--file", action="append", required=True, dest="files")
    command.add_argument("--exclude", action="append", default=[])
    command.add_argument("--external-inputs", help="역할·안전한 버전·복원 한계의 JSON 목록")
    command.add_argument("--base-commit")
    command = commands.add_parser("verify-target", help="보존된 참조 무결성과 현재 명시 입력 비교")
    command.add_argument("--reference", required=True, help="path/sha256 JSON 파일")
    return root


def main(argv=None):
    command_parser = parser()
    args = command_parser.parse_args(argv)
    try:
        if args.command in {"schema", "template"}:
            definition = schema(args.kind)
            result = definition if args.command == "schema" else template(definition)
        else:
            if args.root is None:
                command_parser.error("이 명령은 --root <project/.harness>가 필요합니다")
            store = Store(args.root)
            if args.command == "reserve":
                result = reserve(store.files, args.kind, args.name, args.timezone, args.work_id)
            elif args.command == "reference":
                result = store.files.reference(args.path)
            elif args.command == "put-evidence":
                parts = relative(args.path)
                if len(parts) < 4 or parts[0] != "work" or parts[2] != "evidence":
                    raise RecordError("Raw evidence belongs under work/<work-id>/evidence/")
                validate(parts[1], ID)
                safe_source_path(args.source)
                resolved_parent = args.source.absolute().parent.resolve()
                safe_source_path(resolved_parent / args.source.name)
                source = source_file(resolved_parent, args.source.name)
                if source["kind"] != "file":
                    raise RecordError("Explicit regular evidence source required")
                result = store.files.publish(args.path, source["data"])
            elif args.command == "publish":
                candidate = payload(args.input)
                result = store.publish(candidate)
            elif args.command == "state-update":
                result = update_state(store, payload(args.input), args.expected_revision)
            elif args.command == "state-repair":
                result = repair_state(store, payload(args.input), args.record_id, args.expected_sha256,
                                      args.reason, payload(args.evidence))
            elif args.command == "update-current":
                result = update_current(store, Path(args.input).read_text(), args.expected_sha256)
            elif args.command == "reconcile":
                result = reconcile(store, args.work_id)
            elif args.command == "capture-docs":
                result = capture_documents(store, args.work_id, args.record_id, payload(args.documents))
            elif args.command == "capture-code":
                result = capture_code(store, args.work_id, args.record_id, args.workspace, args.workspace_id,
                                      args.files, args.scope, args.base_commit, args.exclude,
                                      payload(args.external_inputs) if args.external_inputs else None)
            else:
                result = compare_target(store, payload(args.reference))
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
        return 0
    except (RecordError, OSError, KeyError, TypeError, ValueError) as error:
        print(json.dumps({"status": "rejected", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

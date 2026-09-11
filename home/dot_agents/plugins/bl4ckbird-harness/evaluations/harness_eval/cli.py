"""격리된 비교 실행과 실제 근거 기반 판정을 연결한다."""

import argparse
import json
import math
import re
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

from .backend import preflight, run_codex
from .evidence import aggregate, digest, mechanical_checks, snapshot, write_json
from .judging import evaluate, observations
from .scenarios import SCENARIOS, rubric_for

MAX_GLOBAL_INSTRUCTIONS_BYTES = 1_000_000


def source_manifest(root):
    return {str(path.relative_to(root)): digest(path.read_bytes())
            for path in sorted(root.rglob("*")) if path.is_file() and "__pycache__" not in path.parts}


def freeze_global_instructions(candidate, source):
    candidate = Path(candidate)
    if candidate.is_symlink() or not candidate.is_file():
        raise ValueError("전역 지침은 일반 파일이어야 합니다")
    if candidate.stat().st_size > MAX_GLOBAL_INSTRUCTIONS_BYTES:
        raise ValueError("전역 지침이 평가 입력 한도를 초과했습니다")
    destination = source / "global-instructions.md"
    shutil.copyfile(candidate, destination)
    return destination


def build_prompt(case, source, mode):
    prompt = case["request"]
    if mode == "harness":
        prompt += "\n\n적용할 하네스 지침: " + str(source / "skills" / case["entry"]) + " 파일을 읽고 해당 작업에 적용해줘."
        global_instructions = source / "global-instructions.md"
        if global_instructions.is_file():
            prompt += "\n\n보조 전역 지침: " + str(global_instructions) + " 파일을 읽고 이 작업에 적용해줘."
    return prompt


def create_suite(output):
    output.mkdir(parents=True, exist_ok=True)
    date = datetime.now().astimezone().date().isoformat()
    pattern = re.compile(re.escape(date) + r"-(\d+)-evaluation$")
    sequence = max([int(match[1]) for path in output.iterdir() if (match := pattern.fullmatch(path.name))] or [0]) + 1
    while True:
        path = output / ("%s-%03d-evaluation" % (date, sequence))
        try:
            path.mkdir()
        except FileExistsError:
            sequence += 1
        else:
            return path


def trial(args, suite, source, name, mode, repetition):
    case = SCENARIOS[name]
    root = suite / ("%02d-%s-%s" % (repetition, name, mode))
    workspace = root / "workspace"
    workspace.mkdir(parents=True)
    report = {"scenario": name, "mode": mode, "repetition": repetition,
              "status": "unverified", "checks": [], "annotated_question_count": None,
              "question_annotation_coverage": "unverified",
              "question_annotation_limitation": "독립 판정 모델의 질문 열거는 실제 모든 질문 탐지를 보장하지 않음",
              "synthetic_observation": bool(case.get("synthetic_observation"))}
    if report["synthetic_observation"]:
        report["limitations"] = ["Synthetic observation fixture evaluates agent judgment only; it does not establish host integration or prior-session visibility."]
    started = time.monotonic()
    try:
        isolation = preflight(args.codex, workspace, root / "preflight")
        report["isolation"] = isolation
        if isolation["status"] != "satisfied":
            report["checks"] = [{"id": "isolation", "status": "unverified", "reason": "쓰기 경계를 입증하지 못해 모델 호출하지 않음"}]
            return report
        for relative, content in case["files"].items():
            path = workspace / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        before = snapshot(workspace)
        write_json(root / "before.json", before)
        prompt = build_prompt(case, source, mode)
        (root / "request.txt").write_text(prompt, encoding="utf-8")
        rubric = rubric_for(case, mode)
        write_json(root / "rubric.json", rubric)
        run = run_codex(args.codex, workspace, root / "agent", prompt, args.model, args.effort,
                        args.timeout, read_only=case["read_only"])
        report["agent"] = run
        if not run["termination_confirmed"]:
            report["reconciliation_required"] = True
            report["checks"] = [{"id": "execution-ended", "status": "unverified", "reason": "실행 종료 불명. 최종 파일 근거 확정·판정·정리·재사용 보류"}]
            return report
        after = snapshot(workspace)
        write_json(root / "after.json", after)
        if snapshot(workspace) != after:
            report["reconciliation_required"] = True
            report["checks"] = [{"id": "stable-evidence", "status": "unverified", "reason": "사본 보존 중 작업 공간이 변경됨"}]
            return report
        report["checks"] = mechanical_checks(name, before, after)
        report["checks"].append({"id": "execution-completed", "status": "satisfied" if run["status"] == "satisfied" else "unverified",
                                 "reason": "CLI 사건·종료 결과는 agent/metadata.json 참조"})
        if run["status"] == "satisfied":
            evidence = observations(run["paths"]["events"], run["paths"]["final"], before, after)
            judge_workspace = root / "judge-workspace"
            judge_workspace.mkdir()
            judgment = evaluate(run_codex, args.codex, judge_workspace, root / "judge", case["request"],
                                rubric, evidence, args.judge_model, args.judge_effort, args.timeout,
                                required_prompt_text=(source / "skills/harness-review/references/prompts/spec.md").read_text()
                                if name == "spec-review" and mode == "harness" else None)
            report["judge"] = judgment
            report["checks"].extend(judgment["checks"])
            report["annotated_question_count"] = judgment["annotated_question_count"]
            report["question_annotation_coverage"] = judgment["question_annotation_coverage"]
            report["question_annotation_limitation"] = judgment["question_annotation_limitation"]
            if snapshot(workspace) != after:
                report["reconciliation_required"] = True
                report["checks"].append({"id": "post-judgment-stability", "status": "unverified", "reason": "판정 중 대상 변경을 관찰함. 안정된 최종 상태로 보지 않음"})
        else:
            report["checks"].extend({"id": key, "status": "unverified", "reason": "실제 평가 실행 불완전"} for key in rubric)
        report["status"] = aggregate(report["checks"])
    except (OSError, ValueError, TypeError, KeyError) as error:
        report["error"] = str(error)
        report["checks"].append({"id": "evidence-complete", "status": "unverified", "reason": "평가 근거 수집 또는 판정 형식 실패"})
        report["status"] = aggregate(report["checks"])
    finally:
        report["elapsed_seconds"] = time.monotonic() - started
        write_json(root / "result.json", report)
    return report


def run_suite(args):
    plugin = Path(__file__).resolve().parents[2]
    output = args.output.resolve()
    if ".harness" not in output.parts:
        raise ValueError("평가 근거는 .harness 아래에 지정하세요")
    if output == plugin or plugin in output.parents or output in plugin.parents:
        raise ValueError("평가 출력과 플러그인 소스는 겹칠 수 없습니다")
    suite = create_suite(output)
    source = suite / "harness-source"
    ignore_cache = shutil.ignore_patterns("__pycache__")
    for directory in ("skills", "scripts", ".codex-plugin"):
        shutil.copytree(plugin / directory, source / directory, ignore=ignore_cache)
    global_instructions = getattr(args, "global_instructions", None)
    if global_instructions is not None:
        freeze_global_instructions(global_instructions, source)
    sources = source_manifest(source)
    write_json(suite / "source-manifest.json", sources)
    evaluator_sources = source_manifest(plugin / "evaluations")
    write_json(suite / "evaluator-manifest.json", evaluator_sources)
    version = subprocess.run([args.codex, "--version"], capture_output=True, text=True, timeout=20)
    meta = {"schema_version": 1, "instruction_mode": "explicit-file", "global_instructions_included": global_instructions is not None,
            "native_plugin_discovery_tested": False,
            "created_at": datetime.now().astimezone().isoformat(),
            "model": args.model, "effort": args.effort, "judge_model": args.judge_model,
            "judge_effort": args.judge_effort, "timeout_seconds": args.timeout, "repeat": args.repeat,
            "codex_version": version.stdout.strip() if version.returncode == 0 else None,
            "cost": None, "limitations": ["별도 파일로 제공한 스킬 지침 평가. 설치 탐색·메인 실행 루프·세션 간 복구는 미검증",
                                         "기본 모델·도구·전역 스킬 카탈로그 등의 공통 환경 영향은 남을 수 있음",
                                         "의미 판정은 독립 모델의 판단이며 결정적 증명이 아님. 개별 근거를 검토할 수 있음",
                                         "synthetic observation scenario는 주어진 관측에 대한 판단만 평가하며 실제 host 통합·이전 세션 가시성을 입증하지 않음",
                                         "프로세스 그룹 밖의 실행은 호스트 가시성 한계가 있음. 작업 공간을 자동 삭제하지 않음"]}
    write_json(suite / "configuration.json", meta)
    reports = []
    scenarios = args.scenario or list(SCENARIOS)
    modes = ["baseline", "harness"] if args.mode == "paired" else [args.mode]
    print("평가 근거: " + str(suite), flush=True)
    for repetition in range(1, args.repeat + 1):
        for name in scenarios:
            for mode in (modes if repetition % 2 else list(reversed(modes))):
                report = trial(args, suite, source, name, mode, repetition)
                reports.append(report)
                print("%s / %s / %d: %s" % (name, mode, repetition, report["status"]), flush=True)
                calls = [report.get("agent", {})]
                if "judge" in report:
                    calls.append(report["judge"]["run"])
                intact = sources == source_manifest(source) and evaluator_sources == source_manifest(plugin / "evaluations")
                if (report.get("reconciliation_required") or not intact
                        or any(not call.get("termination_confirmed") or call.get("interrupted") for call in calls)):
                    return finish_suite(suite, reports, intact, incomplete=True)
    return finish_suite(suite, reports, sources == source_manifest(source) and evaluator_sources == source_manifest(plugin / "evaluations"))


def finish_suite(suite, reports, source_intact, incomplete=False):
    checks = [{"status": report["status"]} for report in reports]
    if not source_intact:
        checks.append({"status": "failed"})
    if incomplete:
        checks.append({"status": "unverified"})
    status = aggregate(checks)
    summary = {"status": status, "incomplete": incomplete, "source_intact": source_intact,
               "runs": [{k: report.get(k) for k in ("scenario", "mode", "repetition", "status", "annotated_question_count", "question_annotation_coverage", "question_annotation_limitation", "elapsed_seconds", "synthetic_observation")} for report in reports]}
    write_json(suite / "summary.json", summary)
    lines = ["# Evaluation Results", "", "전체 판정: `" + status + "`. 개별 실패·미검증은 아래 결과와 각 실행의 result.json에서 확인한다.", "",
             "| Scenario | Mode | Repetition | Result | Annotated questions | Question annotation coverage | Synthetic observation |", "| --- | --- | --- | --- | --- | --- | --- |"]
    lines.extend("| {scenario} | {mode} | {repetition} | {status} | {annotated_question_count} | {question_annotation_coverage} | {synthetic_observation} |".format(**row) for row in summary["runs"])
    lines += ["", "## Limits", "", "질문 수는 독립 판정 모델이 인용해 열거한 질문 수이며 실제 모든 질문 탐지는 보장하지 않는다. 파일로 제공한 지침의 평가다. 설치 탐색·실행 루프·세션 간 복구는 검증하지 않았다. 호출 원시 이벤트는 검증 근거로 보존하며 사용량·비용 집계는 하지 않는다.", ""]
    (suite / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    print("최종 판정: " + status, flush=True)
    return {"satisfied": 0, "failed": 1, "unverified": 2}[status]


def main(argv=None):
    parser = argparse.ArgumentParser(description="격리 프로젝트에서 하네스 지침의 실제 행동을 비교합니다")
    parser.add_argument("--list", action="store_true", help="모델 호출 없이 시나리오를 나열합니다")
    parser.add_argument("--codex", default="codex")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--model")
    parser.add_argument("--effort", choices=["low", "medium", "high", "xhigh"])
    parser.add_argument("--judge-model")
    parser.add_argument("--judge-effort", choices=["low", "medium", "high", "xhigh"])
    parser.add_argument("--timeout", type=float, help="호출별 평가 제한 시간(초)")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--mode", choices=["paired", "baseline", "harness"], default="paired")
    parser.add_argument("--scenario", action="append", choices=list(SCENARIOS))
    parser.add_argument("--global-instructions", type=Path,
                        help="harness 모드에서만 함께 읽을 전역 지침 일반 파일; suite에 동결 사본을 보존")
    args = parser.parse_args(argv)
    if args.list:
        for name, case in SCENARIOS.items():
            print(name + ": " + case["title"])
        return 0
    for key in ("output", "model", "effort", "judge_model", "judge_effort", "timeout"):
        if getattr(args, key) is None:
            parser.error("필수 인자: --" + key.replace("_", "-"))
    if args.repeat < 1 or not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("반복 횟수와 제한 시간은 양수여야 합니다")
    if args.scenario and len(set(args.scenario)) != len(args.scenario):
        parser.error("같은 시나리오의 반복에는 --repeat를 사용하세요")
    try:
        return run_suite(args)
    except (OSError, ValueError, subprocess.TimeoutExpired) as error:
        parser.exit(2, "평가 시작 실패: " + str(error) + "\n")

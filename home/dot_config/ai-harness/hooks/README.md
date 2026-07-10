# BB Harness 훅

이 스크립트들은 Claude Code나 Codex 훅 시스템을 위한 보수적인 빌딩 블록이다.

기본적으로 전역 설정에 연결되어 있지 않다. 먼저 프로젝트 레벨에서 연결하고, 일상적으로
사용하기에 충분히 조용해진 뒤에만 전역으로 승격한다.

훅이 여전히 필요한 명령을 막는다면 스크립트에 임기응변식 allow 플래그를 추가하지 않는다.
host 도구의 permission이나 escalation 흐름을 사용하거나, 승인된 그 한 작업에 한해 프로젝트
레벨 훅을 의도적으로 비활성화하고 이유를 기록한다.

권장 사용법:

- `block-dangerous-bash.sh`는 파괴적인 셸 명령 체크와 흔한 셸 기반 secret 읽기에 사용.
- `protect-sensitive-read.sh`는 `.env`, private key, credential, secret 파일에 대한 `Read`
  pre-tool 체크에 사용.
- `protect-sensitive-write.sh`는 민감 파일과 직접적인 lockfile 편집에 대한
  `Edit`/`Write`/`MultiEdit` pre-tool 체크에 사용.
- `protect-sensitive-files.sh`는 도구가 아직 read/write 훅을 분리할 수 없을 때 호환성
  wrapper로 사용(`tool_name`에 따라 read/write 스크립트에 위임하므로 패턴은 각각 한 곳에만
  존재).
- `session-context.sh`는 도구가 context-injection 훅을 지원할 때 짧은 세션 시작 context에
  사용.

## 예상 Payload

이 스크립트들은 `PreToolUse` 스타일 훅을 위한 것이다. stdin으로 JSON을 받으며, 단순한
어댑터를 위해 raw text도 허용한다.
`jq`를 사용할 수 없으면 스크립트는 `tool_name`, `file_path`, `path`, Bash `command`에 대해
작은 POSIX `sed` fallback을 사용한다.

공통 필드:

```json
{
  "tool_name": "Read",
  "tool_input": {
    "file_path": ".env"
  }
}
```

Bash의 경우:

```json
{
  "tool_name": "Bash",
  "tool_input": {
    "command": "git reset --hard"
  }
}
```

## 스모크 테스트

```sh
printf '%s' '{"tool_name":"Bash","tool_input":{"command":"git reset --hard"}}' | ./block-dangerous-bash.sh
printf '%s' '{"tool_name":"Bash","tool_input":{"command":"sh -c \"git reset --hard\""}}' | ./block-dangerous-bash.sh
printf '%s' '{"tool_name":"Read","tool_input":{"file_path":".env"}}' | ./protect-sensitive-read.sh
printf '%s' '{"tool_name":"Edit","tool_input":{"file_path":"pnpm-lock.yaml"}}' | ./protect-sensitive-write.sh
```

위 명령은 각각 exit code 2로 종료되어야 한다 — Claude Code의 `PreToolUse` semantics는 exit
2를 "차단, stderr를 Claude에게 전달"로 취급한다. 그 외 0이 아닌 exit는 non-blocking 에러이며
tool call이 계속 진행된다. `.env.example`, `.env.sample`, `.env.template`은 에이전트가
온보딩 템플릿을 확인할 수 있도록 허용된다. 프로젝트별 훅 연결은 전역으로 승격하기 전에
로컬에서 테스트한다.

Bash guard는 각 명령 세그먼트(`;`, `|`, `&`로 분리)를 독립적으로 평가하므로, 한 명령의
플래그가 다른 명령의 패턴을 충족시킬 수 없다:

```sh
printf '%s' '{"tool_name":"Bash","tool_input":{"command":"rm old.txt && grep -rf patterns ."}}' | ./block-dangerous-bash.sh  # exit 0
```

Bash guard는 `.env.example`, `.env.sample`, `.env.template`의 직접 읽기도 허용한다. 실제
`.env` 파일과 `.env.local` 같은 파생 변형은 계속 차단된다.

`-n`이나 `--dry-run`을 사용한 `git clean`은 확인용으로 허용된다. dry-run이 아닌 `git clean`의
force, force push, hard reset, 재귀적 강제 삭제는 반드시 명시적 승인을 거쳐야 한다.

no-`jq` fallback을 검증하려면: macOS 15+는 `/usr/bin/jq`를 기본 포함하므로 `PATH`를 시스템
디렉터리로 줄여도 여전히 jq 경로를 타게 된다. 대신 jq가 없는 도구 디렉터리를 직접 구성한다:

```sh
nojq="$(mktemp -d)"
for t in cat sed grep tr; do ln -s "$(command -v "$t")" "$nojq/"; done
printf '%s' '{"tool_name":"Read","tool_input":{"file_path":".env"}}' | PATH="$nojq" ./protect-sensitive-read.sh
```

## 커버리지와 Gap

훅은 guardrail이지 완전한 보안 통제가 아니다. 이 목록을 프로젝트 레벨 연결을 위한
출발점으로 취급한다.

**훅이 모든 secret 읽기를 막는다고 가정하지 말 것.** Bash guard는 `.env`와 소수의 고정된
credential 파일명 집합에 대한 `cat|less|grep|sed|awk` 직접 읽기(같은 명령 세그먼트 내)만
커버한다. credential key의 *사용*은 의도적으로 허용된다(`ssh -i ~/.ssh/id_rsa`,
`chmod 600 ~/.ssh/id_rsa`), public key(`*.pub`)도 마찬가지다. 여전히 허용되는 우회 경로:
`tail`, `head`, `cp`, 셸 리다이렉션, 언어 인터프리터(`python -c`, `node -e` 등), 아래
Candidate 열에 있는 모든 파일. 이런 경로가 중요하면 프로젝트 레벨 규칙을 연결하거나,
신뢰하기 전에 하니스 스크립트에 프로젝트별 패턴을 추가한다.

| 영역 | 상태 | 비고 |
| --- | --- | --- |
| `.env`, private key, 흔한 credential 파일명 | Covered | Read/write guard가 흔한 직접 접근을 차단. |
| Lockfile | 직접 쓰기에 대해 Covered | 에이전트는 lockfile을 직접 편집하지 말고 패키지 매니저를 사용해야 함. |
| 파괴적인 셸 명령 | 흔한 패턴에 대해 Covered | 프로젝트별 deploy/reload/delete 명령은 추가 규칙이 필요할 수 있음. |
| `.npmrc`, `.pypirc`, `.netrc` | Candidate | 이 파일들이 토큰을 담고 있다면 프로젝트/전역 규칙 추가. |
| Kubernetes config | Candidate | 관련 있다면 `~/.kube/config`나 프로젝트 kubeconfig 경로에 대한 규칙 추가. |
| AWS/GCP/Azure credentials | Candidate | 프로젝트가 사용한다면 클라우드별 credential 경로 추가. |

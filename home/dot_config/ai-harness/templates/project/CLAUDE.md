@AGENTS.md

# Claude Code Wiring

일반 워크플로 내용(스킬 흐름, severity/result vocabulary, second-review 기준)은
`.ai-harness/AGENT_WORKFLOW.md`에 있다 — 여기서 중복하지 않는다. 이 파일은 Claude 전용 wiring만
담는다.

## Reviewer Subagents

`~/.claude/agents/`에 존재할 때 연결되는 Reviewer subagent:

- `implementation-reviewer` — 단일 패스 슬라이스 리뷰: spec compliance (✅/❌) + quality
  (Ready to merge? Yes / With fixes / No).
- `security-reviewer` — diff가 인증, 시크릿, 암호화, 삭제, 신뢰할 수 없는 입력, 민감한 데이터,
  파괴적 작업에 닿을 때.
- `explore-lite` — 저비용 read-only 조회 전용 (저가 모델에 고정).

`second-review`는 전용 Claude subagent가 없다 — 다른 모델의 reviewer가 필요하다. 호스트의
플러그인을 사용해 다른 에이전트로 연결하거나 (예: Claude Code의 Codex 플러그인), 별도 터미널에서
다른 에이전트의 CLI를 실행한다. `~/.config/ai-harness/skills/second-review` 참고.

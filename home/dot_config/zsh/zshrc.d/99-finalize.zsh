# ==========================================
# tmux Auto-attach & Grouped Session Management
# ==========================================

# [Guard Clauses] 예외 환경에서는 tmux 자동 실행을 즉시 중단(return)합니다.

# 1. 이미 tmux 세션 내부에 있는 경우 (무한 루프 방지)
[[ -n "$TMUX" ]] && return

# 2. 사용자 타이핑이 불가능한 비대화형(Non-interactive) 셸인 경우
[[ $- != *i* ]] && return

# 3. VS Code / Antigravity의 백그라운드 환경 변수 로더인 경우
[[ -n "$VSCODE_RESOLVING_ENVIRONMENT" ]] && return

# 4. VS Code / Antigravity의 내장 터미널 창을 연 경우 (이중 실행 방지)
[[ "$TERM_PROGRAM" == "vscode" || "$TERM_PROGRAM" == "antigravity" ]] && return

# ---------------------------------------------------------
# 위 방어선을 모두 통과했다면 순수 터미널(Ghostty 등) 환경입니다.
# ---------------------------------------------------------

if tmux has-session -t main 2>/dev/null; then
    local ATTACHED=$(tmux display-message -p -t main '#{session_attached}' 2>/dev/null)

    if [[ "$ATTACHED" -eq 0 ]]; then
        exec tmux attach-session -t main
    else
        exec tmux new-session -t main -s "main-$$" \; set-option -t "main-$$" destroy-unattached on
    fi
else
    exec tmux new-session -s main
fi

# ==========================================
# tmux Auto-attach & Grouped Session Management
# ==========================================
if [[ -z "$TMUX" ]] && [[ "$TERM_PROGRAM" != "vscode" ]]; then
    # 1. 원본 'main' 세션이 이미 백그라운드에 존재하는지 확인
    if tmux has-session -t main 2>/dev/null; then

    # 2. main 세션을 쳐다보고 있는 활성 창(Client)의 개수를 추출
    local ATTACHED=$(tmux display-message -p -t main '#{session_attached}' 2>/dev/null)

    if [[ "$ATTACHED" -eq 0 ]]; then
        # 3-A. 아무도 안 보고 있다면(실수로 껐거나 모두 Detach 됨): 원본 main으로 바로 접속
        exec tmux attach-session -t main
    else
        # 3-B. 이미 다른 창에서 보고 있다면(거울 모드 방지): 시점을 분리하는 임시 그룹 세션 생성
        exec tmux new-session -t main -s "main-$$" \; set-option -t "main-$$" destroy-unattached on
    fi
  else
        # 4. 세션이 아예 없으면 최초의 main 세션 생성
        exec tmux new-session -s main
  fi
fi

if (( $+commands[fzf] )); then
    # 느린 기본 find 대신 빠르고 .gitignore를 존중하는 fd를 FZF 기본 엔진으로 설정
    export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
    export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
    # OPT+C(디렉토리 이동) 시에는 디렉토리(-t d)만 검색하도록 전용 엔진 분리
    export FZF_ALT_C_COMMAND='fd --type d --hidden --follow --exclude .git'

    # 전역 UI 레이아웃 설정
    # 리버스 레이아웃(아래에서 위로) 적용 및 화면의 40%만 차지하도록 제한
    export FZF_DEFAULT_OPTS="--height 40% --layout=reverse --border --info=inline"

    # XDG 규격에 맞춘 히스토리 파일 저장을 위해 디렉토리 존재 보장
    [ -d "$XDG_STATE_HOME/fzf" ] || mkdir -p "$XDG_STATE_HOME/fzf"
    export FZF_DEFAULT_OPTS="$FZF_DEFAULT_OPTS --history=$XDG_STATE_HOME/fzf/history"

    # 프리뷰(Preview) 창 연동 (bat, eza 활용)
    # CTRL+T 파일 검색 시 bat을 통해 구문 강조가 적용된 파일 내용 미리보기 제공
    export FZF_CTRL_T_OPTS="--preview 'bat -n --color=always {}'"
    # OPT+C 디렉토리 검색 시 eza를 통해 해당 디렉토리 내부 구조 트리 미리보기 제공
    export FZF_ALT_C_OPTS="--preview 'eza -T -L 2 --icons=always {}'"
fi

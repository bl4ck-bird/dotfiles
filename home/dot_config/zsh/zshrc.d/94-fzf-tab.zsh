# ===================================================================
# [Config] fzf-tab 플러그인 zstyle 설정
# ===================================================================
# Zsh의 기본 Tab 자동 완성 메뉴를 FZF 인터페이스로 완벽히 대체(가로채기)합니다.
# compinit(93번)에 의해 자동 완성 시스템이 켜진 후, 플러그인이 로드(95번)되기 전에
# zstyle을 통해 FZF 연동 방식 및 미리보기(Preview) 동작을 정의합니다.
#
# - cd **<TAB> 입력 시 eza를 통한 하위 디렉토리 트리 미리보기 연동 완료

zstyle ':completion:*' insert-tab false
zstyle ':completion:*' menu select
zstyle ':fzf-tab:complete:cd:*' fzf-preview 'eza -1 --color=always $realpath'

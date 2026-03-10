# 사용자 로컬 바이너리 경로
export PATH="$XDG_BIN_HOME:$PATH"

# PATH 배열 내의 중복된 경로를 제거 (가장 먼저 선언된 순서 유지)
typeset -gU path PATH

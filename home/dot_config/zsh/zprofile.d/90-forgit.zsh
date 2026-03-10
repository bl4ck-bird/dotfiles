# Pager 설정 (bat 연동)
# diff나 log 확인 시 기본 텍스트 대신 bat을 사용하여 구문 강조(Syntax Highlighting) 적용
export FORGIT_PAGER='bat -l git -p'

# FZF UI 옵션 커스텀
# forgit 창이 화면 전체를 덮지 않고, 아래에서 위로 올라오는 리버스 레이아웃 적용
export FORGIT_FZF_DEFAULT_OPTS="
--exact
--border
--cycle
--reverse
--height '80%'
"

# Enter 동작 후 FZF 창 유지 여부 (선택 사항)
# 파일을 add(ga)한 후 창을 닫지 않고 계속 다른 파일을 add하고 싶을 때 유용함
# export FORGIT_KEEP_DIRTY_FILES=1

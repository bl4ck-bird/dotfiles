# ===================================================================
# [Config] zsh-history-substring-search 플러그인 옵션 및 바인딩
# ===================================================================
# 입력된 문자열(Substring)이 포함된 과거 명령어를 방향키로 탐색합니다.
# 플러그인이 로드(95번)되면서 생성한 'history-substring-search-up/down' 위젯을
# 실제 물리적 키보드의 방향키 시퀀스와 최종적으로 연결(Mapping)하는 핵심 파일입니다.

# 퍼지 검색 활성화
export HISTORY_SUBSTRING_SEARCH_FUZZY=1

# 검색 결과 하이라이트 컬러
export HISTORY_SUBSTRING_SEARCH_HIGHLIGHT_FOUND='bg=magenta,fg=white,bold'
export HISTORY_SUBSTRING_SEARCH_HIGHLIGHT_NOT_FOUND='bg=red,fg=white,bold'

# 중복 결과 무시
export HISTORY_SUBSTRING_SEARCH_ENSURE_UNIQUE=1

# 방향키 시퀀스(^[[A, ^[[B) 매핑
bindkey '^[[A' history-substring-search-up
bindkey '^[[B' history-substring-search-down

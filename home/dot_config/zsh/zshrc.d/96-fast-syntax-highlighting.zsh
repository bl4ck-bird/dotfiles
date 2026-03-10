# ===================================================================
# [Config] fast-syntax-highlighting 플러그인 테마 오버라이딩
# ===================================================================
# 터미널에 입력되는 텍스트가 일반 명령어인지, Alias인지, 존재하지 않는 경로인지
# 실시간으로 판별하여 시각적 피드백을 제공합니다.
# 플러그인이 로드된 직후 내부 변수(FAST_HIGHLIGHT_STYLES)를 조작하여
# 가독성을 높이는 커스텀 색상을 강제 주입합니다.

# 1. 커스텀 하이라이트 스타일 정의
# 명령어 정체에 따른 색상 분리 (가독성 증대)
typeset -A FAST_HIGHLIGHT_STYLES

FAST_HIGHLIGHT_STYLES[command]='fg=cyan'           # 일반 명령어
FAST_HIGHLIGHT_STYLES[alias]='fg=green,bold'       # Alias (중요도 높음)
FAST_HIGHLIGHT_STYLES[function]='fg=green'         # 쉘 함수
FAST_HIGHLIGHT_STYLES[path]='fg=blue,underline'    # 파일 및 디렉토리 경로
FAST_HIGHLIGHT_STYLES[single-hyphen-option]='fg=yellow' # -a 같은 짧은 옵션
FAST_HIGHLIGHT_STYLES[double-hyphen-option]='fg=yellow' # --help 같은 긴 옵션
FAST_HIGHLIGHT_STYLES[variable]='fg=172'           # 환경 변수 ($PATH 등)

# 2. 비대화형 쉘에서의 오버헤드 방지
# (스크립트 실행 중에는 하이라이팅을 끄고 CPU 자원 보존)
if [[ -z "$PS1" ]]; then
    FAST_HIGHLIGHT_STYLES=()
fi

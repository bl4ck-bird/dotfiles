# Alias 출처 저장을 위한 전역 연관 배열 선언
typeset -A _alias_sources

# Alias 중복 감지 및 안전 등록 래퍼 함수
safe_alias() {
    local alias_name="${1%%=*}"
    local current_caller="${funcfiletrace[1]%:*}"
    current_caller="${current_caller#$ZDOTDIR/}"

    if (( $+aliases[$alias_name] )); then
        local original_source="${_alias_sources[$alias_name]:-알 수 없는 소스}"

        print -u2 "\e[33m[경고] Alias 충돌 감지: '$alias_name'\e[0m"
        print -u2 "  - 기존 정의: \e[32m$original_source\e[0m"
        print -u2 "  - 중복 시도: \e[31m$current_caller\e[0m"
        print -u2 "------------------------------------------------"
    fi

    # 출처 기록 및 실제 Alias 등록
    _alias_sources[$alias_name]="$current_caller"
    alias -- "$@"
}

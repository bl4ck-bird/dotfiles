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

# Tool Update
function tool-upgrade() {
    local DEEP_CLEAN=false
    if [[ "$1" == "--deep-clean" ]]; then
        DEEP_CLEAN=true
    fi

    # 1. Homebrew 파이프라인
    if command -v brew >/dev/null 2>&1; then
        echo "==> [1/2] Updating Homebrew..."
        brew update
        brew upgrade

        echo "==> Cleaning up Homebrew..."
        if [ "$DEEP_CLEAN" = true ]; then
            brew cleanup -s --prune=all
        else
            brew cleanup
        fi
    else
        echo "==> [1/2] Homebrew is not installed. Skipping..."
    fi

    # 2. Mise 파이프라인
    if command -v mise >/dev/null 2>&1; then
        echo "==> [2/2] Updating Mise..."
        mise plugin update
        mise upgrade

        echo "==> Cleaning up Mise..."
        mise prune -y
        if [ "$DEEP_CLEAN" = true ]; then
            local M_CACHE="${MISE_CACHE_DIR:-${XDG_CACHE_HOME:-$HOME/.cache}/mise}"
            local M_DATA_DL="${MISE_DATA_DIR:-${XDG_DATA_HOME:-$HOME/.local/share}/mise}/downloads"

            [[ -d "$M_CACHE" ]] && rm -rf "$M_CACHE"/*
            [[ -d "$M_DATA_DL" ]] && rm -rf "$M_DATA_DL"/*
        fi
    else
        echo "==> [2/2] Mise is not installed. Skipping..."
    fi

    echo "==> ✅ tools update complete."
}

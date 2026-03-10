#!/bin/bash

export PATH="$HOME/.local/bin:$PATH"

COLOR_RED='\033[0;31m'
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_BLUE='\033[1;34m'
COLOR_CYAN='\033[1;36m'
COLOR_RESET='\033[0m'

echo_color() {
    local COLOR="$1"
    local TEXT="$2"
    echo -e "${COLOR}${TEXT}${COLOR_RESET}"
}

print_color_box_title() {
    local COLOR="$1"
    local WIDTH="$2"
    local TITLE_TEXT="┤ $3 ├"
    local CONTENTS_TEXT="$4"
    local TITLE_LEFT=$(( (WIDTH - ${#TITLE_TEXT}) / 2 ))
    local TITLE_RIGHT=$(( WIDTH - ${#TITLE_TEXT} - TITLE_LEFT ))

    local TITLE_LEFT_DASH=$(printf "%*s" $((TITLE_LEFT - 1)) "")
    local TITLE_RIGHT_DASH=$(printf "%*s" $((TITLE_RIGHT - 1)) "")
    printf "${COLOR}┌%s%s%s┐${COLOR_RESET}\n" "${TITLE_LEFT_DASH// /─}" "$TITLE_TEXT" "${TITLE_RIGHT_DASH// /─}"

    while IFS= read -r line || [[ -n "$line" ]]; do
        printf "${COLOR}│ %-*s │${RESET}\n" $((WIDTH - 4)) "$line"
    done <<< "$CONTENTS_TEXT"

    printf "${COLOR}└%*s┘${COLOR_RESET}\n" $(($WIDTH - 2)) "" | tr ' ' '─'
}

print_color_box_center() {
    local COLOR="$1"
    local WIDTH="$2"
    local RAW_TEXT="$3"

    printf "${COLOR}┌%*s┐${COLOR_RESET}\n" $(($WIDTH - 2)) "" | tr ' ' '─'

    while IFS= read -r line || [[ -n "$line" ]]; do
        local TEXT=" $line "
        local LEFT=$(( (WIDTH - ${#TEXT}) / 2 ))
        local RIGHT=$(( WIDTH - ${#TEXT} - LEFT ))

        printf "${COLOR}│%*s%s%*s│${COLOR_RESET}\n" $((LEFT - 1)) "" "$TEXT" $(( RIGHT - 1 )) ""
    done <<< "$RAW_TEXT"

    printf "${COLOR}└%*s┘${COLOR_RESET}\n" $(($WIDTH - 2)) "" | tr ' ' '─'
}

homebrew_shellenv() {
    if ! command -v brew &> /dev/null; then
        if [[ -x "/opt/homebrew/bin/brew" ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
        elif [[ -x "/usr/local/bin/brew" ]]; then
            eval "$(/usr/local/bin/brew shellenv)"
        fi
    fi
}
homebrew_check() {
    homebrew_shellenv

    if ! command -v brew &> /dev/null; then
        echo_color $COLOR_RED "Homebrew: Not found."
        exit 1
    fi
}

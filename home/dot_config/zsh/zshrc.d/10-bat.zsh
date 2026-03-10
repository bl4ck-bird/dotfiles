if (( $+commands[bat] )); then
    safe_alias cat="bat --style=plain --paging=never"
    safe_alias c="bat"
    safe_alias ocat="\cat"
fi

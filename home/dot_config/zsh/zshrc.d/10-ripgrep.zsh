if (( $+commands[rg] )); then
    safe_alias rgh="rg --hidden"
    safe_alias fgrep="rg --line-number --no-heading --color=always --smart-case"
fi

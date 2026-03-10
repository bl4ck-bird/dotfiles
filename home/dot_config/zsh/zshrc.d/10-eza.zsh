if (( $+commands[eza] )); then
    safe_alias ll="eza -l -g --icons=auto"
    safe_alias la="eza -la -g --icons=auto"
    safe_alias lt="eza -la --sort=modified --reverse --icons=auto"
    safe_alias ltree="eza --tree --level=2 --icons=auto"
fi

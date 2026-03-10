if (( $+commands[fd] )); then
    safe_alias fd="fd --hidden"
elif (( $+commands[fdfind] )); then
    safe_alias fd="fdfind --hidden"
fi

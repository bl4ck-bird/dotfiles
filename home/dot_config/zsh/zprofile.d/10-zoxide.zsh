if (( $+commands[zoxide] )); then
    export _ZO_DATA_DIR="$XDG_DATA_HOME/zoxide"
    [[ -d "$_ZO_DATA_DIR" ]] || mkdir -p "$_ZO_DATA_DIR"
fi

if (( $+commands[opencode] )); then
    export OPENCODE_CONFIG_DIR="$XDG_CONFIG_HOME/opencode"
    export OPENCODE_DATA_DIR="$XDG_DATA_HOME/opencode"
    export OPENCODE_CACHE_DIR="$XDG_CACHE_HOME/opencode"

    [[ -d "$OPENCODE_CONFIG_DIR" ]] || mkdir -p "$OPENCODE_CONFIG_DIR"
    [[ -d "$OPENCODE_DATA_DIR" ]] || mkdir -p "$OPENCODE_DATA_DIR"
    [[ -d "$OPENCODE_CACHE_DIR" ]] || mkdir -p "$OPENCODE_CACHE_DIR"
fi

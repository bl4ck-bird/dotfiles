if (( $+commands[mise] )); then
    export MISE_CONFIG_DIR="$XDG_CONFIG_HOME/mise"
    export MISE_CACHE_DIR="$XDG_CACHE_HOME/mise"
    export MISE_STATE_DIR="$XDG_STATE_HOME/mise"
    export MISE_DATA_DIR="$XDG_DATA_HOME/mise"
    [[ -d "$MISE_CONFIG_DIR" ]] || mkdir -p "$MISE_CONFIG_DIR"
    [[ -d "$MISE_CACHE_DIR" ]] || mkdir -p "$MISE_CACHE_DIR"
    [[ -d "$MISE_STATE_DIR" ]] || mkdir -p "$MISE_STATE_DIR"
    [[ -d "$MISE_DATA_DIR" ]] || mkdir -p "$MISE_DATA_DIR"

    eval "$(mise env)"
fi

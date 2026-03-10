ZCOMPDUMP="$XDG_CACHE_HOME/zsh/.zcompdump-$ZSH_VERSION"
ZCOMPCACHE="$XDG_CACHE_HOME/zsh/zcompcache"
[[ -d "${ZCOMPDUMP:h}" ]] || mkdir -p "${ZCOMPDUMP:h}"
[[ -d "$ZCOMPCACHE" ]] || mkdir -p "$ZCOMPCACHE"

zstyle ':completion:*' use-cache yes
zstyle ':completion:*' cache-path "$ZCOMPCACHE"

fpath=("$ZCOMP_HOME" $fpath)

need_rebuild=false
[[ -n ${^fpath}(N-nt$ZCOMPDUMP) || ! -f "$ZCOMPDUMP" ]] && need_rebuild=true

autoload -Uz compinit
if [[ "$need_rebuild" == true ]]; then
    rm -f "$ZCOMPDUMP" "${ZCOMPDUMP}.zwc"
    compinit -d "$ZCOMPDUMP"
else
    compinit -C -d "$ZCOMPDUMP"
fi

[[ "$ZCOMPDUMP" -nt "${ZCOMPDUMP}.zwc" || ! -f "${ZCOMPDUMP}.zwc" ]] && zcompile "$ZCOMPDUMP"

for cmd_args in $_DEFERRED_COMPDEFS; do
    compdef ${=cmd_args}
    echo "compdef ${=cmd_args}"
done

unset need_rebuild

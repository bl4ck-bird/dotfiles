#!/bin/bash
input=$(cat)

MODEL=$(echo "$input"  | jq -r '.model.display_name // "claude"' | sed -E 's/ *\([^)]*context\)//')
CWD=$(echo "$input"    | jq -r '.workspace.current_dir // .cwd // ""')
CTX=$(echo "$input"    | jq -r '.context_window.used_percentage // 0' | cut -d. -f1)
CTX_USED=$(echo "$input" | jq -r '
  (.context_window.current_usage.input_tokens // 0)
  + (.context_window.current_usage.cache_creation_input_tokens // 0)
  + (.context_window.current_usage.cache_read_input_tokens // 0)
')
CTX_MAX=$(echo "$input"  | jq -r '.context_window.context_window_size // 0')
RATE5H=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // "—"' | cut -d. -f1)
RATE7D=$(echo "$input" | jq -r '.rate_limits.seven_day.used_percentage // "—"' | cut -d. -f1)
RESET5H=$(echo "$input" | jq -r '.rate_limits.five_hour.resets_at // empty')
RESET7D=$(echo "$input" | jq -r '.rate_limits.seven_day.resets_at // empty')

# git branch (silent if not a repo)
BRANCH=""
if [[ -n "$CWD" ]]; then
  BRANCH=$(git -C "$CWD" symbolic-ref --short HEAD 2>/dev/null)
fi

# 5h countdown: NhNm (minute precision) — e.g. "2h15m" / "45m"
fmt_short() {
  local ts=$1 now diff mins hours rem_m
  [[ -z "$ts" ]] && return
  now=$(date +%s)
  diff=$(( ts - now ))
  (( diff <= 0 )) && return
  mins=$(( diff / 60 ))
  hours=$(( mins / 60 ))
  rem_m=$(( mins - hours * 60 ))
  if (( hours == 0 )); then
    echo " (${mins}m)"
  else
    echo " (${hours}h${rem_m}m)"
  fi
}

# 7d countdown: <48h → Nh, else NdNh
fmt_long() {
  local ts=$1 now diff mins hours days rem_h
  [[ -z "$ts" ]] && return
  now=$(date +%s)
  diff=$(( ts - now ))
  (( diff <= 0 )) && return
  mins=$(( diff / 60 ))
  hours=$(( mins / 60 ))
  days=$(( hours / 24 ))
  if (( hours < 48 )); then
    echo " (${hours}h)"
  else
    rem_h=$(( hours - days * 24 ))
    echo " (${days}d${rem_h}h)"
  fi
}

RESET5H_STR=$(fmt_short "$RESET5H")
RESET7D_STR=$(fmt_long  "$RESET7D")

# ANSI colors
DIM='\033[2m'
BOLD='\033[1m'
CYAN='\033[36m'
MAGENTA='\033[35m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
RESET='\033[0m'

color_for() {
  local v=$1
  if ! [[ "$v" =~ ^[0-9]+$ ]]; then echo "$DIM"; return; fi
  if   (( v >= 80 )); then echo "$RED"
  elif (( v >= 50 )); then echo "$YELLOW"
  else echo "$GREEN"
  fi
}

# Humanize token count: 1234 → 1.2k, 1234567 → 1.2M
fmt_tokens() {
  local n=$1
  if (( n >= 1000000 )); then
    awk -v n="$n" 'BEGIN { v = n/1000000; printf (v >= 10 ? "%dM" : "%.1fM"), v }'
  elif (( n >= 1000 )); then
    awk -v n="$n" 'BEGIN { v = n/1000; printf (v >= 10 ? "%dk" : "%.1fk"), v }'
  else
    echo "$n"
  fi
}

CTX_USED_H=$(fmt_tokens "$CTX_USED")
CTX_MAX_H=$(fmt_tokens "$CTX_MAX")

CTX_C=$(color_for "$CTX")
R5_C=$(color_for "$RATE5H")
R7_C=$(color_for "$RATE7D")

GIT_PART=""
if [[ -n "$BRANCH" ]]; then
  GIT_PART=" ${DIM}│${RESET} ${MAGENTA}⎇ ${BRANCH}${RESET}"
fi

# Suffix % only on numeric rate values; placeholders render bare.
fmt_rate() {
  local v=$1
  [[ "$v" =~ ^[0-9]+$ ]] && echo "${v}%" || echo "$v"
}
RATE5H_STR=$(fmt_rate "$RATE5H")
RATE7D_STR=$(fmt_rate "$RATE7D")

printf "${BOLD}${CYAN}%s${RESET}${GIT_PART} ${DIM}│${RESET} ctx ${CTX_C}%s/%s${RESET} ${DIM}(%s%%)${RESET} ${DIM}│${RESET} 5h ${R5_C}%s${RESET}${DIM}%s${RESET} ${DIM}·${RESET} 7d ${R7_C}%s${RESET}${DIM}%s${RESET}\n" \
  "$MODEL" "$CTX_USED_H" "$CTX_MAX_H" "$CTX" "$RATE5H_STR" "$RESET5H_STR" "$RATE7D_STR" "$RESET7D_STR"

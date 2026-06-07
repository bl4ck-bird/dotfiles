# ~/.config/direnv/lib/10-layout_uv.sh
#
# Usage (project .envrc):
#   layout uv
#
# Python version is controlled by a .python-version file in the project
# (uv reads it automatically). This function only creates/activates the venv.

layout_uv() {
  # uv must be available (managed by mise in this setup)
  if ! has uv; then
    log_error "layout uv: 'uv' not found in PATH"
    return 1
  fi

  # Re-evaluate when version/lock files change
  watch_file .python-version pyproject.toml uv.lock

  # Create .venv if it doesn't exist (uv honors .python-version)
  if [[ ! -d ".venv" ]]; then
    log_status "layout uv: creating virtualenv via 'uv venv'"
    uv venv || { log_error "layout uv: 'uv venv' failed"; return 1; }
  fi

  # Activate: put .venv/bin on PATH and export VIRTUAL_ENV
  export VIRTUAL_ENV="$PWD/.venv"
  PATH_add "$VIRTUAL_ENV/bin"
  export UV_ACTIVE=1
}

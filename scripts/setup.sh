#!/usr/bin/env bash
set -Eeuo pipefail
trap cleanup SIGINT SIGTERM ERR EXIT

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd -P)
REPO_DIR=$(dirname "$SCRIPT_DIR")

usage() {
  cat <<EOF
USAGE: $(basename "${BASH_SOURCE[0]}")

Sets up the local environment for dev work.

AVAILABLE OPTIONS:

-h, --help      Print this help and exit
-v, --verbose   Print script debug info
EOF
}

cleanup() {
  trap - SIGINT SIGTERM ERR EXIT
}

msg() {
  echo >&2 -e "${1-}"
}

fail() {
  local msg=$1
  local code=${2-1}
  msg "${RED}$msg${NOFORMAT}"
  printf "\n"
  usage
  exit "$code"
}

parse_params() {
  args=()
  while [[ $# -gt 0 ]]; do
    case "$1" in
      -h | --help) usage && exit 0 ;;
      -v | --verbose) set -x ;;
      -?*) fail "Unknown option: $1" ;;
      *) args+=("$1") ;;
    esac
    shift
  done
  return 0
}

setup_colors() {
  if [[ -t 2 ]] && [[ -z "${NO_COLOR-}" ]] && [[ "${TERM-}" != "dumb" ]]; then
    NOFORMAT="\033[0m" RED="\033[0;31m" BLUE="\033[0;34m" GREEN='\033[0;32m'
  else
    NOFORMAT="" RED="" BLUE="" GREEN=""
  fi
}

validate_dependencies_exist() {
  local dependencies=(
    "pre-commit"
    "python"
  )

  for dependency in "${dependencies[@]}"; do
    if ! command -v "$dependency" &>/dev/null; then
      fail "Missing dependency: $dependency"
    fi
  done
}

main() {
  setup_colors
  parse_params "$@"

  if command -v "mise"; then
    msg "${BLUE}🔍 mise detected; configuring runtimes...${NOFORMAT}"
    mise install -y
  fi

  # Check if we're running in Python a virtual environment (creating one if not):
  if [[ -z "${VIRTUAL_ENV-}" ]]; then
    msg "${BLUE}🚜 Creating Python virtual environment...${NOFORMAT}"
    python -m venv "$REPO_DIR/.venv"
    # shellcheck disable=SC1091
    source "$REPO_DIR/.venv/bin/activate"
  fi

  msg "${BLUE}🚜 Installing dependencies...${NOFORMAT}"
  if ! command -v "pip" &>/dev/null; then
    python -m ensurepip
  fi
  if ! command -v "uv" &>/dev/null; then
    # shellcheck disable=SC1087
    python -m pip install "$REPO_DIR[build]"
  fi
  uv sync --extra all

  msg "${BLUE}🚜 Installing pre-commit hooks...${NOFORMAT}"
  pre-commit install

  # At this stage, we should have all of our dependencies installed; confirm that:
  validate_dependencies_exist

  msg "${GREEN}✅ Setup complete!${NOFORMAT}"
}

main "$@"

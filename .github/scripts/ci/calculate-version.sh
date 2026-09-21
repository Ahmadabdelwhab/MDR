#!/usr/bin/env bash
set -euo pipefail

previous=$(git tag --list 'v*' --sort=-version:refname \
  | grep -E '^v[0-9]+\.[0-9]+\.[0-9]+$' \
  | head -n 1 || true)

bump() {
  local base="${previous#v}" major minor patch
  IFS='.' read -r major minor patch <<< "$base"
  case "$1" in
    major) echo "v$((major + 1)).0.0" ;;
    minor) echo "v${major}.$((minor + 1)).0" ;;
    patch) echo "v${major}.${minor}.$((patch + 1))" ;;
  esac
}

version=ci
is_release=false

if [ "$EVENT_NAME" = "push" ] && [[ "$REF" == refs/tags/v* ]]; then
  version="$REF_NAME"
  is_release=true
elif [ "$EVENT_NAME" = "push" ] && [ "$REF_NAME" = "main" ]; then
  version="${previous:+$(bump patch)}"
  version="${version:-v0.1.0}"
  is_release=true
elif [ "$EVENT_NAME" = "workflow_dispatch" ] && [ "$REF_NAME" = "main" ]; then
  version="${previous:+$(bump "${RELEASE_TYPE:-patch}")}"
  version="${version:-v0.1.0}"
  [ "${DRY_RUN:-true}" = "false" ] && is_release=true
fi

echo "version=$version" >> "$GITHUB_OUTPUT"
echo "previous_tag=$previous" >> "$GITHUB_OUTPUT"
echo "is_release=$is_release" >> "$GITHUB_OUTPUT"
echo "Version: $version (previous: ${previous:-none}, release: $is_release)"

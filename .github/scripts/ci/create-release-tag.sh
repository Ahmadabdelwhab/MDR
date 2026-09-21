#!/usr/bin/env bash
set -euo pipefail

git fetch --tags --force
if git rev-parse "refs/tags/$VERSION" >/dev/null 2>&1; then
  echo "Release tag $VERSION already exists"
  exit 0
fi

git tag "$VERSION" "$GITHUB_SHA"
git push origin "refs/tags/$VERSION"
echo "Created release tag $VERSION"

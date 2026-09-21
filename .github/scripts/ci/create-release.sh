#!/usr/bin/env bash
set -euo pipefail

if [ -n "${PREVIOUS_TAG:-}" ]; then
  range="${PREVIOUS_TAG}..HEAD"
else
  range=HEAD
fi

{
  echo "# MDR ${VERSION}"
  echo
  echo "## Changes"
  echo
  git log --no-merges --pretty=format:'- %s (%h)' "$range" || echo "- Initial release"
  echo
  echo
  echo "## Docker image"
  echo
  echo '```'
  echo "docker pull ${IMAGE_NAME}:${VERSION}"
  echo '```'
  echo
  echo "## Binaries"
  echo
  echo "- Linux: mdr-${VERSION}-linux"
  echo "- macOS: mdr-${VERSION}-macos"
  echo "- Windows: mdr-${VERSION}-windows.exe"
  echo
  echo 'Verify downloads against `SHA256SUMS`.'
  if [ -n "${PREVIOUS_TAG:-}" ]; then
    echo
    echo "**Full diff**: ${GITHUB_SERVER_URL}/${GITHUB_REPOSITORY}/compare/${PREVIOUS_TAG}...${VERSION}"
  fi
} > release-notes.md

cat release-notes.md
if gh release view "$VERSION" >/dev/null 2>&1; then
  gh release upload "$VERSION" release-assets/* --clobber
  gh release edit "$VERSION" --notes-file release-notes.md
else
  gh release create "$VERSION" release-assets/* --notes-file release-notes.md
fi

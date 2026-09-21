#!/usr/bin/env bash
set -euo pipefail

version_number="${VERSION#v}"
for tag in "$VERSION" "$version_number" "sha-${GITHUB_SHA}" latest; do
  docker tag mdr:ci "${IMAGE_NAME}:${tag}"
  docker push "${IMAGE_NAME}:${tag}"
done

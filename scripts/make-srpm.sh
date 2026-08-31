#!/usr/bin/env bash
# Assemble an SRPM from a spec in rpm/ plus the shared patches/ and the pinned
# Source0 tarball. Usage: scripts/make-srpm.sh rpm/<spec> <outdir>
set -euo pipefail
spec="${1:?spec path}"; outdir="${2:?output dir}"
repo="$(cd "$(dirname "$0")/.." && pwd)"
work="$(mktemp -d)"; trap 'rm -rf "$work"' EXIT
mkdir -p "$work"/{SPECS,SOURCES,SRPMS}
cp "$repo/$spec" "$work/SPECS/"
cp "$repo"/patches/*.patch "$work/SOURCES/" 2>/dev/null || true
( cd "$work/SOURCES" && spectool -g -S "$work/SPECS/$(basename "$spec")" )
mkdir -p "$outdir"
rpmbuild --define "_topdir $work" -bs "$work/SPECS/$(basename "$spec")"
cp "$work"/SRPMS/*.src.rpm "$outdir"/
echo "SRPM(s) in $outdir:"; ls -1 "$outdir"/*.src.rpm

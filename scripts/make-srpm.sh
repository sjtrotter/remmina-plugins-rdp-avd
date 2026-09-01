#!/usr/bin/env bash
# Assemble an SRPM from a spec plus the shared patches/ and the pinned Source0.
# Usage: scripts/make-srpm.sh <spec> <outdir>
#   <spec> may be absolute (as COPR's make_srpm passes) or relative to the repo.
set -euo pipefail
spec="${1:?spec path}"; outdir="${2:?output dir}"
repo="$(cd "$(dirname "$0")/.." && pwd)"
# resolve the spec: absolute/CWD-relative first, then repo-relative
if [ -f "$spec" ]; then specfile="$(cd "$(dirname "$spec")" && pwd)/$(basename "$spec")"
elif [ -f "$repo/$spec" ]; then specfile="$repo/$spec"
else echo "spec not found: $spec" >&2; exit 1; fi
work="$(mktemp -d)"; trap 'rm -rf "$work"' EXIT
mkdir -p "$work"/{SPECS,SOURCES,SRPMS}
cp "$specfile" "$work/SPECS/"
cp "$repo"/patches/*.patch "$work/SOURCES/" 2>/dev/null || true
( cd "$work/SOURCES" && spectool -g -S "$work/SPECS/$(basename "$specfile")" )
mkdir -p "$outdir"
rpmbuild --define "_topdir $work" -bs "$work/SPECS/$(basename "$specfile")"
cp "$work"/SRPMS/*.src.rpm "$outdir"/
echo "SRPM(s) in $outdir:"; ls -1 "$outdir"/*.src.rpm

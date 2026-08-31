# Base commit, patch series, and how to verify

## One pinned base

Everything builds from a single Remmina commit, pinned in `sources.json`:

- commit `c620366ed3fe1b7218a21b6d32f9c975b243b7031` (`git describe
  v1.4.43-144-gc620366ed3`), EVR `1.4.43^144.gc620366ed3-1`.
- Chosen because it carries the RDP **AAD web-auth** base
  (`plugins/rdp/rdp_web_auth.c`) that the plugin extends, which the bare
  `v1.4.43` release tag does **not** have, and because this exact snapshot has
  been validated end-to-end on hardware.

The base spec and the plugin spec use the **same** commit so the plugin is
ABI-matched to the base (`Requires: remmina = <exact EVR>`).

## Patch base — resolved (no rebase)

`patches/` was `git format-patch`-exported from the fork branch
`contrib/eitaas-series-v5` against master `c620366ed` (`v1.4.43-144-gc620366ed`),
which is the base pinned above. All 7 patches apply cleanly to it (verified with
`patch -p1` on a pristine export). The base pin was moved 2 commits forward from
the older `030946c8` (`v1.4.43-142`) snapshot the downstream bundle used — those
2 intervening upstream commits touched the same `rdp_file.c`/`rdp_plugin.c` lines
patch 0001 edits, which is why the series did not apply to the older commit.
Nothing needs rebasing.

## Verify before release

```
# 1) series applies to the pinned base
tar xf Remmina-c620366ed….tar.gz && cd Remmina-c620366ed…
for p in ../patches/00*.patch; do patch -p1 < "$p"; done   # must be clean

# 2) both RPMs build (Fedora 44 / mock or rpmbuild) — see .github/workflows/ci.yml
scripts/make-srpm.sh rpm/remmina.spec               out/
scripts/make-srpm.sh rpm/remmina-plugins-rdp-avd.spec out/
mock -r fedora-44-x86_64 out/remmina-*.src.rpm
mock -r fedora-44-x86_64 out/remmina-plugins-rdp-avd-*.src.rpm

# 3) plugin %check asserts FreeRDP3 + WebKit2GTK4.1 linkage and the
#    smartcard-auth / p11tool / PKCS#11 strings are present in the .so
```

Hardware validation (real Gov AVD + PIV card) is a separate, human-run gate.

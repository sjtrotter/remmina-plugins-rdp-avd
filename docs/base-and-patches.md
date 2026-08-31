# Base commit, patch series, and how to verify

## One pinned base

Everything builds from a single Remmina commit, pinned in `sources.json`:

- commit `030946c83fe1b7218a21b6d32f9c975b243b7031` (`git describe
  v1.4.43-142-g030946c83`), EVR `1.4.43^142.g030946c83-1`.
- Chosen because it carries the RDP **AAD web-auth** base
  (`plugins/rdp/rdp_web_auth.c`) that the plugin extends, which the bare
  `v1.4.43` release tag does **not** have, and because this exact snapshot has
  been validated end-to-end on hardware.

The base spec and the plugin spec use the **same** commit so the plugin is
ABI-matched to the base (`Requires: remmina = <exact EVR>`).

## Open item: rebase the series onto the pinned base

`patches/` was `git format-patch`-exported from the GitLab fork branch
`contrib/eitaas-series-v5` (head `2f5e58e5b`) against master `c620366ed`.
Master changed `plugins/rdp/rdp_file.c` and `rdp_plugin.c` between `c620366ed`
and `030946c8`, so the series **does not apply** to the pinned base as-is:

```
$ patch -p1 --dry-run < patches/0001-RDP-preserve-protected-RDPW-settings.patch
Hunk #1 succeeded at 37 with fuzz 2.
Hunk #2 FAILED at 90.
Hunk #3 FAILED at 191.
```

**Fix (one-time):** rebase the series onto `030946c8` on the fork and re-export.

```
# in the Remmina fork checkout
git rebase --onto 030946c83f <series-base> contrib/eitaas-series-v5
#   resolve rdp_file.c / rdp_plugin.c conflicts (the intended result is known:
#   it matches the behavior already proven by the downstream queue on 030946c8)
git format-patch --no-numbered-parent 030946c83f..HEAD -o /path/to/patches/
```

## Verify before release

```
# 1) series applies to the pinned base
tar xf Remmina-030946c8….tar.gz && cd Remmina-030946c8…
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

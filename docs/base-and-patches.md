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

## Verified locally (2026-08-31)

Against a pristine `c620366ed` export with all 7 patches applied and FreeRDP 3.31:

- all 7 patches apply clean (`patch -p1`);
- `remmina-plugin-rdp` compiles with `-DWITH_RDP_AUTH_AAD=ON -DWITH_SSO_MIB=OFF`;
- the `.so` links `libfreerdp3.so.3` + `libwebkit2gtk-4.1.so.0` and contains the
  `smartcard-auth:` reason codes, `p11tool`, and PKCS #11 certificate handling
  (the plugin `%check` assertions), plus the AVD Gov constants
  (`login.microsoftonline.us`, `wvd.azure.us`).

The plugin `%build` disables every `find_suggested_package()` core-app dependency
the RDP plugin does not use (gcrypt, libvncserver, cups, appindicator, avahi, …);
without that, configure fails in a clean chroot because Remmina treats suggested
packages as REQUIRED unless `-DWITH_<PKG>=OFF`. A full `mock`/COPR build against
the distribution FreeRDP is the remaining CI step.

## Why a base Remmina package is required (ABI) — verified 2026-08-31

The plugin is compiled from 1.4.43 source and is ABI-locked to it
(`Requires: remmina = <exact EVR>`). This is **not** optional and the base
cannot be dropped for a plugin-only package against stock distro Remmina:

- Between Remmina **1.4.41** (Fedora stock) and **1.4.43**, `RemminaPluginService`
  gained 5 methods, **appended** to the struct:
  `plugin_multimon_monitor_count`, `plugin_multimon_monitor_info`,
  `plugin_multimon_monitor_drawing_area`,
  `plugin_multimon_monitor_set_drawing_area`, `plugin_multimon_main_monitor_index`.
- The RDP plugin **calls these in 14 places** (`plugins/rdp/rdp_monitor.c`,
  `plugins/rdp/rdp_event.c`) on core connection/event paths.
- Those offsets are past the end of 1.4.41's shorter struct, so a 1.4.43-built
  plugin on stock 1.4.41 would call out-of-bounds function pointers → crash.

Naming: the base is **vanilla** Remmina (no patches, `WITH_RDP_AUTH_AAD` off) —
so it is named `remmina`, not `remmina-webkit`/`-avd`; all WebKit/AAD/PIV code is
in the plugin. It replaces stock Remmina under the `remmina-next` model (EVR
sorts above stock, below the next real release).

**This is temporary.** Because the struct only appends, once a distro's own
Remmina reaches >= 1.4.43 the plugin loads on it directly and the base can be
dropped (ship plugin-only, `Requires: remmina >= 1.4.43`). Track each distro's
Remmina version; retire the base per-distro as it catches up.

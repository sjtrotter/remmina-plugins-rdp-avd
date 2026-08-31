# CI/CD and distribution — how the outputs are built and published

Two stages: **CI** validates every change on GitHub; **CD** publishes the RPMs
through COPR (Fedora), with PPA/AUR to follow. GitHub is the *source of truth*;
COPR is the *builder and host*. This mirrors how `remmina-next` and
ungoogled-chromium ship.

```
 GitHub repo (this)                 COPR project sjtrotter/remmina-plugins-rdp-avd
 ─────────────────                  ───────────────────────────────────────────────
 push / PR ─► GitHub Actions CI     tag / push ─► webhook ─► COPR builds 2 packages:
   • patches apply to pinned base                    • remmina            (base)
   • plugin SRPM builds + %check                     • remmina-plugins-rdp-avd (plugin)
   • (nightly) base SRPM builds                   ─► dnf copr enable … ; dnf install
```

## CI (GitHub Actions, `.github/workflows/ci.yml`) — the gate

Runs in a `fedora:44` container on every push/PR:
1. **patch-check** — download the pinned base tarball (`sources.json`), apply
   `patches/*` with `patch -p1`. Fails if the series drifts from the base.
2. **plugin-rpm** — `scripts/make-srpm.sh rpm/remmina-plugins-rdp-avd.spec`,
   `dnf builddep` it, `rpmbuild --rebuild`. The spec's `%check` asserts the
   `.so` links FreeRDP3 + WebKit2GTK-4.1 and carries the smart-card strings.
   This is the real correctness gate; it links the **distribution** FreeRDP.
3. **base-rpm** *(heavier; nightly or `workflow_dispatch`)* — build the base
   `remmina` SRPM/RPM so base drift is caught without spending CI minutes on
   every PR.

CI does **not** publish. No secrets required for the gate.

## CD (COPR) — the publisher

COPR project `sjtrotter/remmina-plugins-rdp-avd` with **two packages**, each
using COPR's SCM/`make_srpm` method against this repo:

| COPR package | spec | SRPM command |
|---|---|---|
| `remmina` | `rpm/remmina.spec` | `make -f .copr/Makefile srpm SPEC=rpm/remmina.spec` |
| `remmina-plugins-rdp-avd` | `rpm/remmina-plugins-rdp-avd.spec` | `make -f .copr/Makefile srpm SPEC=rpm/remmina-plugins-rdp-avd.spec` |

- **Chroots:** `fedora-44`, `fedora-rawhide` (`x86_64`; add `aarch64` later).
- **Trigger:** a GitHub webhook on push to `main`/tags rebuilds both packages.
- **Install-time ordering:** the plugin `Requires: remmina = <exact EVR>`; both
  packages live in the one COPR, so `dnf copr enable sjtrotter/remmina-plugins-rdp-avd`
  then `dnf install remmina-plugins-rdp-avd` pulls the base from the same repo
  and its `Obsoletes` swaps the stock RDP plugin. Builds are independent (the
  plugin does not need the base to *build*), so no build-order constraint.
- **Alternative** (more control, needs a secret): a `release.yml` that runs
  `copr-cli build` with a `COPR_API_TOKEN` GitHub secret on tag. Prefer the
  webhook unless we need Actions to own publishing.

## Releases / versioning

The package version tracks the base: `1.4.43^144.gc620366ed`. Cut a repo tag
(`git tag vYYYY.MM.DD` or semver) whenever the **base commit** or the **patch
series** changes; the tag triggers the COPR rebuild and, optionally, a GitHub
Release carrying the two SRPMs for non-COPR users. Bump the plugin `Release:`
(and the base changelog) in the same commit as any patch change.

## Debian/Ubuntu (PPA) and Arch (AUR) — to follow

- **PPA / OBS:** `deb/` will hold `debian/` packaging + a Launchpad recipe or an
  openSUSE OBS project. Targets need FreeRDP ≥ 3.16, so Ubuntu 26.04+; Debian 13
  (3.15) and Ubuntu 24.04 (3.5) are below the floor — use the portable bundle
  there. Same two-artifact shape (base + plugin) because stock Debian/Ubuntu
  Remmina also lacks the AAD web-auth base.
- **AUR:** `arch/` will hold a `PKGBUILD` that builds base + plugin and
  `provides`/`conflicts` the stock packages. AUR hosts only the PKGBUILD; users
  build locally.

## Hardware gate

Green CI + a successful COPR build are necessary but not sufficient: a human
runs the full flow (import a real AVD `.rdpw`, PIV cert + PIN, reach the desktop)
on real hardware before a release is announced. The de-branded plugin is
behaviorally equivalent to the hardware-tested downstream build but is a distinct
binary, so it re-validates.

# remmina-plugins-rdp-avd

A drop-in replacement for Remmina's RDP plugin that adds **Azure Virtual Desktop
(Entra/AAD) authentication** with **smart-card (PIV) web sign-in**, plus the
matching Remmina base it needs. Install stock Remmina's world, swap in this one
plugin, and an Azure Virtual Desktop `.rdpw` — including US Government cloud —
imports as a normal connection you click to open, signing in through the
embedded web view with a PIV certificate and PIN.

This repository is the **source of truth for the community packages** (COPR for
Fedora; PPA for Debian/Ubuntu and AUR for Arch to follow). Its outputs:

1. **A Remmina base build** (`rpm/remmina.spec`) — vanilla Remmina at a pinned
   snapshot, ABI-matched to the plugin. Emits the usual `remmina` +
   `remmina-plugins-{rdp,vnc,exec,secret,…}` set.
2. **The plugin package** `remmina-plugins-rdp-avd` (`rpm/remmina-plugins-rdp-avd.spec`)
   — the patched `remmina-plugin-rdp.so`, `Provides`/`Obsoletes`/`Conflicts`
   the stock `remmina-plugins-rdp`, linked against the distribution's own
   FreeRDP 3.
3. **A declared minimum Remmina** (`sources.json` → `minimum_versions`).

## Minimum versions — and why we ship our own base

- **Remmina:** this repo's base package (`1.4.43^144.gc620366ed`). The plugin
  extends Remmina's RDP **AAD web-auth** path (`plugins/rdp/rdp_web_auth.c`),
  which is **absent from every *released* Remmina** — it lives on master after
  the v1.4.43 tag. **No stock distro Remmina can host this plugin**, so the
  community repo ships its own Remmina base on every distro (not just Fedora).
- **FreeRDP:** `>= 3.16.0` (adds `GatewayAvdScope` / `GatewayAvdAccessAadFormat`);
  tested against `3.30.0`. Linked against the distribution's FreeRDP 3 — not
  vendored.

## Layout

```
patches/     de-branded RDP series (SSOT) — equivalent to the Remmina upstream MR candidates
rpm/         remmina.spec (base) + remmina-plugins-rdp-avd.spec (plugin)
deb/ arch/   PPA / AUR packaging (to follow)
docs/        avd-cloud-constants.md (constants + provenance), rdp-file-parity.md, base-and-patches.md
scripts/     make-srpm.sh (assemble an SRPM from a spec + patches/ + Source0)
.copr/       COPR build entry
```

## Status

All 7 patches apply cleanly to the pinned base `c620366ed` (`v1.4.43-144`);
see `docs/base-and-patches.md`. Remaining before a release: build both SRPMs +
mock build (`.github/workflows/ci.yml`) and a human-run hardware validation on a
real Gov AVD + PIV card (the de-branded plugin is behaviorally equivalent to the
hardware-tested downstream build but is a distinct binary, so it re-validates).

## Relationship to upstream Remmina

The `patches/` series is the same work proposed to Remmina as merge requests
(smart-card web sign-in; OAuth hardening; `.rdpw` import; AVD/Gov-cloud
selection). As those land upstream, the delta here shrinks. This repo carries no
product branding, private paths, or bundle lifecycle — only public cloud
constants and generic Remmina/FreeRDP integration.

## License

GPL-2.0-or-later (Remmina-derived) with the OpenSSL linking exception. See
`LICENSE` and `LICENSE.OpenSSL`.

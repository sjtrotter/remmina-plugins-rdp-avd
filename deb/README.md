# Debian/Ubuntu packaging (PPA) — to follow

Same model as the RPMs: a Remmina base at the pinned commit (with the RDP
AAD web-auth code) plus a `remmina-plugin-rdp-avd` binary that Provides/Replaces
`remmina-plugin-rdp`, built against the distro's FreeRDP 3 (>= 3.16). Debian 13
(FreeRDP 3.15) and Ubuntu 24.04 (3.5) are below the floor and are not targets
for the plugin variant; use the portable bundle there.

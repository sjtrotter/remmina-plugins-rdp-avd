# RDP `.rdp`/`.rdpw` importer & settings parity

FreeRDP recognizes ~105 `.rdp` keys; Remmina's importer maps ~21. This is the
plan (and permanent log) for closing that gap in the importer and the New-Profile
editor. Planned as one Remmina MR with three commits: (1) importer-only wins,
(2) `selectedmonitors` apply fix, (3) new settings. Not yet in `patches/`.

Classes: **IMPORT-ONLY** = Remmina already has the field + apply code, only the
importer branch is missing. **NEW-SETTING** = needs a `RemminaProtocolSetting`
entry (+ apply code) + importer branch. **OUT** = no clean FreeRDP/Remmina path
(logged below with the reason so it is never silently reconsidered).

## Commit 1 — IMPORT-ONLY (one `remmina_rdp_file_import_field` branch each)
Clean: `use multimon`→`multimon`, `usbdevicestoredirect`→`usb`,
`redirectcomports`→`shareserial`, `redirectwebauthn`→`sharewebauthn`,
`connection type`→`network` (verify value list = FreeRDP `CONNECTION_TYPE_*`),
`autoreconnection enabled`→`disableautoreconnect` (inverted).
Deferred to commit 3 (value semantics interact): `audiocapturemode`,
`drivestoredirect` (add a "redirect all drives" toggle), and the security keys
`enablecredsspsupport` / `negotiate security layer` (both drive the existing
`security` dropdown — import must interpret the combination, not add toggles).

## Commit 2 — `selectedmonitors` apply fix (bugfix)
`monitorids` (MONITOR_LIST) already exists in the GUI but
`remmina_rdp_monitor_define()` never reads it → `FreeRDP_MonitorIds` is never
set. Fix the apply path + add the `selectedmonitors` import branch.

## Commit 3 — NEW-SETTING (RemminaProtocolSetting + apply + import)
Display/scaling: `dynamic resolution`, `smart sizing`, `desktopscalefactor`.
Redirection: `videoplaybackmode`, `redirectlocation`, `camerastoredirect`
(with `encode redirected video capture` + `redirected video capture encoding
quality` as camera modifiers, not standalone), `devicestoredirect`.
Cache/network: `bitmapcachepersistenable`, `network auto detect`
(`bandwidthautodetect`+`networkautodetect` → one setting).
Gateway/Kerberos: `kdcproxyname`, `rdgiskdcproxy`. Credentials:
`prompt for credentials`. RemoteApp: `remoteapplicationcmdline`,
`remoteapplicationfile`, `remoteapplicationicon`.

Design hold (owner): the 7 performance-flag keys (`compression`,
`disable wallpaper`, `allow font smoothing`, `allow desktop composition`,
`disable full window drag`, `disable menu anims`, `disable themes`) are driven
today by Remmina's `quality`/`network` presets; exposing them per-key conflicts
with that model. Left OUT unless done as a 3-value (Default/On/Off) override —
a separate proposal, not this MR.

## OUT — documented, not implemented (with reason)
| Key | Reason |
|---|---|
| `maximizetocurrentdisplays`, `singlemoninwindowedmode` | FreeRDP `// TODO`, no setting |
| `disableconnectionsharing`, `displayconnectionbar`, `enableworkspacereconnect` | no FreeRDP setting exists |
| `redirectposdevices` | FreeRDP block reuses `RedirectComPorts`, no independent effect |
| `disable cursor setting`, `winposstr`, `use redirection server name` | FreeRDP parses but never applies |
| `remoteapplicationexpandcmdline`, `remoteapplicationexpandworkingdir` | parsed, not wired by FreeRDP file.c |
| `screen mode id` | window/fullscreen is Remmina's own concern |
| `desktop size id` | overlaps `desktopwidth`/`desktopheight`, already imported via `resolution` |

Counts: IMPORT-ONLY 10, NEW-SETTING 26, OUT 13 (of the 49-key documented gap).

# Azure cloud constants — values and provenance

The plugin never learns the sign-in server from a profile. It recognizes the
**gateway host's public DNS suffix** and applies the matching cloud's
**public, vetted OAuth constants**, which are compiled in. This document is the
human-readable provenance for those constants; the code SSOT is
`patches/0002-RDP-select-Azure-US-Government-AVD-authentication.patch`
(`plugins/rdp/rdp_avd_cloud.h`).

## The table (`remmina_avd_clouds()`)

| Row | `gateway_suffix` | `authority` | `scope` (decoded) | `redirect_format` |
|-----|------------------|-------------|-------------------|-------------------|
| Commercial (default) | *(none)* | `login.microsoftonline.com` | `https://www.wvd.microsoft.com/.default openid profile offline_access` | `https://<authority>/<tenant>/oauth2/nativeclient` |
| US Government | `.wvd.azure.us` | `login.microsoftonline.us` | `https://www.wvd.azure.us/.default openid profile offline_access` | `https://login.microsoftonline.com/common/oauth2/nativeclient` |

Selection (`remmina_avd_cloud_for_gateway(host)`): return the row whose
`gateway_suffix` is a suffix of `FreeRDP_GatewayHostname` (`g_str_has_suffix`);
otherwise `NULL` → FreeRDP's own default (commercial). The values FreeRDP reads
are `FreeRDP_GatewayAzureActiveDirectory` (authority),
`FreeRDP_GatewayAvdScope`, and `FreeRDP_GatewayAvdAccessAadFormat`. Nothing is
copied from the profile; an authority already set to something other than the
commercial default is left untouched.

## Provenance — how we know each value is correct

**Commercial row — inherited from FreeRDP, not chosen by us.** FreeRDP ships
`login.microsoftonline.com` + scope `https://www.wvd.microsoft.com/.default` +
client id `a85cf173-4192-42f8-81fa-777a763e6e2c` hardcoded in its AVD/ARM
gateway auth path. The commercial row simply mirrors FreeRDP's default.

**US Government authority `login.microsoftonline.us` — Microsoft-documented.**
Microsoft's Azure Government guidance states that for Azure Government / M365
GCC High / DoD, **only `https://login.microsoftonline.us` should be used as the
authority** (migrated from the older `login-us.microsoftonline.com`).
- https://devblogs.microsoft.com/azuregov/azure-government-aad-authority-endpoint-update/
- https://learn.microsoft.com/en-us/azure/azure-government/documentation-government-plan-identity

**US Government scope `https://www.wvd.azure.us/.default` — sovereign analog.**
FreeRDP's commercial `www.wvd.microsoft.com/.default` with the documented Azure
Government AVD namespace substitution `microsoft.com → azure.us`; `.wvd.azure.us`
is Microsoft's documented required-FQDN namespace for Gov AVD.
- https://learn.microsoft.com/en-us/azure/virtual-desktop/required-fqdn-endpoint

**Empirical confirmation — real hardware.** The full flow authenticated
end-to-end against a live US Government AVD tenant with a PIV smart card. A wrong
authority or scope fails at the IdP with a specific, well-known error —
`AADSTS900439 USGClientNotSupportedOnPublicEndpoint` (Gov client hitting the
commercial authority, or vice-versa). That error was never observed; the desktop
was reached.
- https://learn.microsoft.com/en-us/troubleshoot/entra/entra-id/app-integration/error-aadsts900439-usgclientnotsupportedonpublicendpoint

## Why suffix-matched, not read from the file (security)

If an untrusted `.rdpw` could name the OAuth authority, a hostile file could aim
a smart-card-backed sign-in — and its token — at an attacker-controlled IdP. By
deriving the authority only from the gateway's public namespace (which is also
the host the connection physically reaches), a hostile file can at most select
among the real Azure clouds we recognize. Unrecognized gateway → commercial
default → fail closed.

## Maintenance

Only Commercial + US Government are covered today. A new sovereign cloud (e.g.
Azure China `.wvd.azure.cn`) would need a new row with that cloud's documented
authority/scope; until added, such gateways fall to commercial and fail closed.

_Related upstream context: FreeRDP #10656 "Accessing Azure Government AVD
Workspace with smartcard" corroborates the endpoints and the use case._

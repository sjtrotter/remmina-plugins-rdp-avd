# remmina-plugins-rdp-avd — drop-in RDP plugin with Azure Virtual Desktop
# (Entra/AAD) support and smart-card (PIV) web sign-in.
#
# A drop-in replacement for the stock/base remmina-plugins-rdp. It adds the
# Azure AD (Entra) embedded WebKit sign-in and a PKCS #11 smart-card (PIV)
# client-certificate picker + PIN entry during that sign-in, imports signed AVD
# .rdpw profiles, selects the Azure US Government authority/scope/redirect by
# gateway namespace, and binds the OAuth transaction (state + PKCE S256, exact
# redirect). Certificate verification stays on; no PINs, tokens, PKCS #11 URIs,
# or card labels are logged. See docs/ and README.md.
#
# Built from the SAME pinned Remmina base source (sources.json) as the companion
# remmina.spec, so the plugin is ABI-matched to that Remmina, and linked against
# the distribution's own FreeRDP 3 (>= 3.16 for the AVD gateway APIs; tested
# 3.30). WITH_RDP_AUTH_AAD=ON / WITH_SSO_MIB=OFF (WebKit browser path only).
#
# The only file installed is the patched remmina-plugin-rdp.so; the RDP emblem
# icons are shipped by the core `remmina` package.

%global commit c620366ed85def5c3de2549eec7fcbef577281d8
%global base_version 1.4.43^144.gc620366ed
%global base_release 1%{?dist}
# The remmina-plugins-rdp capability EVR this package provides/obsoletes: one
# release above the base plugin (release 1) so a plain `dnf install` obsoletes
# BOTH the stock plugin and the equal-versioned base plugin, without ever
# obsoleting its own provide.
%global rdp_evr %{base_version}-2%{?dist}

Name: remmina-plugins-rdp-avd
Version: %{base_version}
Release: 1%{?dist}
Summary: Drop-in Remmina RDP plugin with Azure Virtual Desktop + smart-card (PIV) web sign-in
# Remmina (GPL-2.0-or-later, OpenSSL exception) + smart-card integration
# (GPL-2.0-or-later).
License: GPL-2.0-or-later
URL: https://github.com/sjtrotter/remmina-plugins-rdp-avd

# Same pinned Remmina base snapshot as the companion remmina.spec
# (sha256 in sources.json).
Source0: https://gitlab.com/Remmina/Remmina/-/archive/%{commit}/Remmina-%{commit}.tar.gz

# De-branded RDP patch series (SSOT: patches/ in this repo; equivalent to the
# Remmina upstream merge-request candidates). A change to one is applied to all.
Patch0: 0001-RDP-preserve-protected-RDPW-settings.patch
Patch1: 0002-RDP-select-Azure-US-Government-AVD-authentication.patch
Patch2: 0003-RDP-honor-configured-AVD-scope-and-redirect-format.patch
Patch3: 0004-RDP-bind-and-own-OAuth-callback-results.patch
Patch4: 0005-RDP-handle-PKCS11-client-certificates-in-WebKit.patch
Patch5: 0006-RDP-extend-ARM-gateway-response-timeout.patch
Patch6: 0007-RDP-test-the-protected-connection-file-helpers.patch

BuildRequires: cmake >= 3.2
BuildRequires: gcc-c++
BuildRequires: gettext
BuildRequires: intltool
BuildRequires: pkgconfig(freerdp3) >= 3.16.0
BuildRequires: pkgconfig(gtk+-3.0)
BuildRequires: pkgconfig(json-glib-1.0)
BuildRequires: pkgconfig(libsecret-1)
BuildRequires: pkgconfig(libsoup-3.0)
BuildRequires: pkgconfig(libssh) >= 0.8.0
BuildRequires: pkgconfig(libpcre2-8)
BuildRequires: pkgconfig(webkit2gtk-4.1)
BuildRequires: pkgconfig(x11)
BuildRequires: pkgconfig(xkbfile)
BuildRequires: pkgconfig(libcurl)
BuildRequires: binutils
BuildRequires: libsodium-devel

# ABI lock: compiled against this exact Remmina build (as stock plugins-rdp
# pins "Requires: remmina = EVR"); a different remmina build may change the ABI.
Requires: remmina%{?_isa} = %{base_version}-%{base_release}

# Clean drop-in swap of the stock/base RDP plugin.
Provides: remmina-plugins-rdp = %{rdp_evr}
Provides: remmina-plugins-rdp%{?_isa} = %{rdp_evr}
Obsoletes: remmina-plugins-rdp < %{rdp_evr}
Conflicts: remmina-plugins-rdp

# Smart-card sign-in runtime helpers (the plugin builds and every non-PIV
# connection works without them): p11tool lists the card's certificates
# (searched in PATH at run time); opensc provides the PKCS #11 module.
Recommends: gnutls-utils
Recommends: opensc

%description
%{summary}.

Drop-in replacement for the stock Remmina RDP plugin (remmina-plugins-rdp) that
adds Azure Virtual Desktop / Entra (Azure AD) authentication with an embedded
WebKit sign-in window, and a PKCS #11 smart-card (PIV) client-certificate picker
and PIN entry inside that window. It imports signed AVD .rdpw profiles, selects
the Azure US Government authority/scope/redirect by gateway namespace, and binds
the OAuth transaction (state + PKCE S256, exact redirect). Certificate
verification stays on; no PINs, tokens, PKCS #11 URIs, or card labels are logged.

Built from the same pinned Remmina base source as the companion `remmina`
package and links the distribution's FreeRDP 3 and WebKit2GTK 4.1.

%prep
%autosetup -p1 -n Remmina-%{commit}

%build
# Same base flags as the vanilla remmina build, plus AAD + PIV web sign-in
# (WITH_SSO_MIB=OFF: WebKit browser path only). Only the RDP plugin is built.
# The monorepo configure treats find_suggested_package() deps as REQUIRED
# unless disabled (WITH_<PKG>=OFF), so every core-app dependency the RDP plugin
# does not use is turned off here — otherwise configure fails in a clean chroot
# on gcrypt/libvncserver/cups/appindicator/avahi even though only the RDP
# plugin target is built. Verified: with these flags the plugin builds against
# only this spec's BuildRequires.
%cmake \
    -DCMAKE_INSTALL_LIBDIR=%{_lib} \
    -DCMAKE_INSTALL_PREFIX=%{_prefix} \
    -DWITH_FREERDP3=ON \
    -DWITH_RDP=ON \
    -DWITH_RDP_AUTH_AAD=ON \
    -DWITH_SSO_MIB=OFF \
    -DWITH_GETTEXT=ON \
    -DWITH_NEWS=OFF \
    -DWITH_KIOSK_SESSION=OFF \
    -DWITH_GCRYPT=OFF \
    -DWITH_LIBVNCSERVER=OFF \
    -DWITH_CUPS=OFF \
    -DWITH_AVAHI=OFF \
    -DHAVE_LIBAPPINDICATOR=OFF \
    -DWITH_SPICE=OFF \
    -DWITH_WWW=OFF \
    -DWITH_X2GO=OFF \
    -DWITH_KF5WALLET=OFF \
    -DWITH_VTE=OFF \
    -DWITH_PYTHONLIBS=OFF
%cmake_build --target remmina-plugin-rdp

%install
install -d %{buildroot}%{_libdir}/remmina/plugins
install -p -m 0755 \
    %{_vpath_builddir}/plugins/rdp/remmina-plugin-rdp.so \
    %{buildroot}%{_libdir}/remmina/plugins/remmina-plugin-rdp.so

%check
so=%{buildroot}%{_libdir}/remmina/plugins/remmina-plugin-rdp.so
echo "== NEEDED libraries =="
readelf -d "$so" | grep NEEDED
readelf -d "$so" | grep -q 'libfreerdp3.so.3'   || { echo "FAIL: not linked to libfreerdp3.so.3"; exit 1; }
readelf -d "$so" | grep -q 'libwebkit2gtk-4.1'  || { echo "FAIL: not linked to libwebkit2gtk-4.1"; exit 1; }
echo "== smart-card auth strings =="
strings "$so" | grep -q 'smartcard-auth:'                    || { echo "FAIL: missing smartcard-auth reason codes"; exit 1; }
strings "$so" | grep -q 'p11tool'                            || { echo "FAIL: missing p11tool reference"; exit 1; }
strings "$so" | grep -qi 'g_tls_certificate_new_from_pkcs11' || { echo "FAIL: missing PKCS#11 certificate handling"; exit 1; }
echo "OK: linkage and smart-card strings present"

%files
%license LICENSE
%{_libdir}/remmina/plugins/remmina-plugin-rdp.so

%changelog
* Mon Aug 31 2026 remmina-plugins-rdp-avd <noreply@example.invalid> - 1.4.43^144.gc620366ed-1
- Initial drop-in AVD/PIV RDP plugin variant.
- Built from the pinned Remmina base snapshot with the de-branded RDP series,
  WITH_RDP_AUTH_AAD=ON / WITH_SSO_MIB=OFF, against the distribution FreeRDP 3.30
  and WebKit2GTK 4.1.
- Provides/Obsoletes/Conflicts remmina-plugins-rdp for a clean swap.

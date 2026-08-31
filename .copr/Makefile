# COPR builds one package per spec. Point each COPR package at this repo with the
# "make_srpm" method and set SPEC to the spec to build, e.g.:
#   SPEC=rpm/remmina.spec
#   SPEC=rpm/remmina-plugins-rdp-avd.spec
SPEC ?= rpm/remmina-plugins-rdp-avd.spec
srpm:
	dnf -y install rpm-build rpmdevtools || true
	scripts/make-srpm.sh $(SPEC) $(outdir)

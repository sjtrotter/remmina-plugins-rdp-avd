# COPR make_srpm invokes:
#   make -f .copr/Makefile srpm outdir="<dir>" spec="<abs path to the package's spec>"
# `spec` is the package's "Spec File" field (e.g. rpm/remmina.spec or
# rpm/remmina-plugins-rdp-avd.spec) as an absolute path. Each COPR package sets
# its own spec, so one Makefile serves both packages.
spec ?= rpm/remmina-plugins-rdp-avd.spec
outdir ?= .

srpm:
	dnf -y install rpm-build rpmdevtools || true
	./scripts/make-srpm.sh "$(spec)" "$(outdir)"

#!/usr/bin/make -f

CFLAGS := $(shell DEB_BUILD_OPTIONS=hardening=+all dpkg-buildflags --get CFLAGS) -Wno-strict-aliasing
CPPFLAGS := $(shell DEB_BUILD_OPTIONS=hardening=+all dpkg-buildflags --get CPPFLAGS)
LDFLAGS := $(shell DEB_BUILD_OPTIONS=hardening=+all dpkg-buildflags --get LDFLAGS) -Wl,--as-needed

DEST := $(shell readlink -f $(CURDIR)/../acpica-tools)
SOURCE = tools/power/acpi

ifneq (default,$(origin CC))
	MF = LD='$$(CC)'
endif

build: distclean
	$(MAKE) -C $(SOURCE) all $(MF) DEBUG=false OPTIMIZATION="$(CFLAGS) $(CPPFLAGS)" \
		LDFLAGS="$(LDFLAGS)"

install:
	$(MAKE) -C $(SOURCE) install $(MF) DEBUG=false OPTIMIZATION="$(CFLAGS) $(CPPFLAGS)" \
		LDFLAGS="$(LDFLAGS)" DESTDIR="$(DEST)"

distclean:
	$(MAKE) -C $(SOURCE) clean

clean:
	rm -rf $(DEST)

.PHONY: build install distclean clean

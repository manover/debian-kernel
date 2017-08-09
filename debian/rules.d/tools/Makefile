SUBDIRS = \
	hv \
	perf \
	power

ifneq ($(DO_USBIP),False)
  SUBDIRS += usb/usbip
endif

include $(top_rulesdir)/Makefile.inc

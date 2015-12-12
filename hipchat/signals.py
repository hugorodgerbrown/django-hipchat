# -*- coding: utf-8 -*-
"""hipchat signal definitions."""
from django.dispatch import Signal

# Signal sent when the app receives a data request from HipChat. The signal
# is fired from within the view function (so inside an HTTP request/response)
# so this *is* performance-bound. The signal is used as a mechanism for
# returning external data - the calling app can connect to the signal,
# and then return a GlanceData object which will be used by the view
# as its return value.
glance_data_requested = Signal(providing_args=['glance'])

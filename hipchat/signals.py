# -*- coding: utf-8 -*-
# signal definitions for hipchat
from django.dispatch import Signal

# Signal sent after profile data has been captured, but before it is
# saved. This signal can be used to cancel the profiling by calling the
# instance.cancel() method, which sets an internal property telling the
# instance not to save itself when capture() is called.
request_profile_complete = Signal(providing_args=['request', 'response', 'instance'])


# Signal sent when the app receives a data request from HipChat. The signal
# is fired from within the view function (so inside an HTTP request/response)
# so this *is* performance-bound. The signal is used as a mechanism for
# returning external data - the calling app can connect to the signal,
# and then return a GlanceData object which will be used by the view
# as its return value.
glance_data_request = Signal(providing_args=['glance'])

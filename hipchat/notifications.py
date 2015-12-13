# -*- coding: utf-8 -*-
"""Wrapper around the HipChat v2 API.

This module contains a couple of generic functions for sending messages
to rooms and users within HipChat. It also contains a python logging
Handler, so that it can be used within logging to pipe warnings and
errors into the Danger Zone room. (HIPCHAT_ERROR_ROOM)

>>> hipchat.send_room_message('Lounge', 'This is a message')
>>> hipchat.send_user_message('hugo', 'Hello, Hugo')

Finally, there are some color-specific helpers to make general-purpose
messaging easy - these will send messages to the room defined in settings
as HIPCHAT_INFO_ROOM.

>>> hipchat.yellow('this is a yellow message')

Messages are sent via RQ, using the settings.QUEUE_HIPCHAT value to determine
whether to send them sync or async.

Requires HIPCHAT_API_TOKEN to be set.

"""
import json
import logging
import os
import random

from django.conf import settings

import requests
# import django_rq

API_V2_ROOT = 'https://api.hipchat.com/v2/'
VALID_COLORS = ('yellow', 'green', 'red', 'purple', 'gray', 'random')
VALID_FORMATS = ('text', 'html')

# requests are sent via a queue
# HIPCHAT_QUEUE = django_rq.get_queue(async=settings.QUEUE_HIPCHAT)
logger = logging.getLogger(__name__)


def get_token():
    """Get a valid 'personal' auth token.

    The HipChat API is rate limited, and the advice from the support team
    is that we either build a proper HipChat Connect app (which will take
    time, although may the way ahead), OR we use a set of tokens, each of
    which is a valid user token. To this end, instead of having a single
    HIPCHAT_API_TOKEN value, we also have a HIPCHAT_API_TOKENS (plural)
    value, which contains comma-separated token. This function returns
    a random token from the set available, so that in theory we can
    'load-balance' the usage.

    """
    tokens = os.getenv('HIPCHAT_API_TOKENS', '').split(',')
    token = random.choice(tokens)
    # if we don't have a choice, use the default
    if token == '':
        return settings.HIPCHAT_API_TOKEN
    else:
        # strip any trailing spaces
        return token.strip()


class HipChatError(Exception):

    """Custom error raised when communicating with HipChat API."""

    def __init__(self, status_code, error_message):
        # super(HipChatError, self).__init__(message)
        self.status_code = status_code
        self.error_message = error_message

    def __unicode__(self):
        message = json.loads(self.error_message).get('error', {}).get('message')
        return u'Status code %s: %s' % (self.status_code, message)

    def __str__(self):
        return unicode(self).decode('utf-8')


def get_auth_headers(auth_token=None):
    """Return authentication headers for API requests.

    Kwargs:
        auth_token: if passed in this is used as the API token. If
            this is None, look in the os.environ for a value for
            'HIPCHAT_API_TOKEN'.

    Returns a dict that can be passed into requests.post as the
        'headers' dict.

    """
    token = auth_token or get_token()
    assert token is not None, (u"No valid HipChat authentication token found.")
    return {
        'Authorization': 'Bearer %s' % token,
        'Host': 'api.hipchat.com',
        'Content-Type': 'application/json'
    }


def _call_api(
        url, message, auth_token=None,
        color='yellow', sender=None, notify=False, message_format='html'):
    """Send message to user or room via API.

    Args:
        url: API endpoint
        message: string, The message body, 1-10000 chars.

    Kwargs:
        auth_token: string, the API auth token to use, defaults to the os.environ
            value for 'HIPCHAT_API_TOKEN'.
        color: string, message background, defaults to 'yellow', can be
            any value in VALID_COLORS
        sender: string, the name that appears as the sender of the message.
            defaults to the name of the owner of the auth token.
        notify: bool, defaults to False, if True then 'ping' recipients.
        message_format: string, one of VALID_FORMATS - the format of the
            message. If 'html' it can contains links etc., but if 'text' it can
                be used for fixed-width-appropriate messages - e.g. code / quotes.

    Raises HipChatError if for any reason the request fails.

    """
    assert message is not None, u"Missing message param"
    assert len(message) >= 1, u"Message too short, must be 1-10,000 chars."
    assert len(message) <= 10000, u"Message too long, must be 1-10,000 chars."
    assert color in VALID_COLORS, u"Invalid color value: %s" % color
    assert message_format in VALID_FORMATS, u"Invalid format: %s" % message_format

    headers = get_auth_headers(auth_token=auth_token)
    data = {
        'message': message,
        'color': color,
        'notify': notify,
        'message_format': message_format
    }
    if sender is not None:
        data['from'] = sender

    resp = requests.post(url, data=json.dumps(data), headers=headers)
    if str(resp.status_code)[:1] != '2':
        raise HipChatError(resp.status_code, resp.text)


def send_room_message(room_id_or_name, message, auth_token=None,
                      color='yellow', sender=None, notify=False,
                      message_format='html'):
    """Send a message to room."""
    assert room_id_or_name not in (None, ''), u"Missing room_id_or_name"
    url = "%sroom/%s/notification" % (API_V2_ROOT, room_id_or_name)
    _call_api(
        url,
        message,
        auth_token=auth_token,
        color=color,
        sender=sender,
        notify=notify,
        message_format=message_format
    )


def send_user_message(user_id_or_email, message, auth_token=None,
                      notify=False, message_format='html'):
    """Send a message to room."""
    assert user_id_or_email not in (None, ''), u"Missing user_id_or_email"
    url = "%suser/%s/message" % (API_V2_ROOT, user_id_or_email)
    _call_api(
        url,
        message,
        auth_token=auth_token,
        notify=notify,
        message_format=message_format
    )


# ================================================
# Colour specific helper functions
# ================================================
def _color(room, message, color):
    """Helper that wraps up sending a colorised room message."""
    return send_room_message(room, message, color=color)


def yellow(room, message, *args):
    """Send a yellow message."""
    return _color(room, message % args, 'yellow')


def gray(room, message, *args):
    """Send a gray message."""
    return _color(room, message % args, 'gray')


def grey(room, message, *args):
    """Send a gray message."""
    return _color(room, message % args, 'gray')


def green(room, message, *args):
    """Send a green message."""
    return _color(room, message % args, 'green')


def purple(room, message, *args):
    """Send a purple message."""
    return _color(room, message % args, 'purple')


def red(room, message, *args):
    """Send a red message."""
    return _color(room, message % args, 'red')

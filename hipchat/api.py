# -*- coding: utf-8 -*-
"""HipChat API interations."""
import json
import requests


class HipChatError(Exception):

    """Custom error raised when communicating with HipChat API."""

    def __init__(self, status_code, error_message):
        # super(HipChatError, self).__init__(message)
        self.status_code = status_code
        self.error_message = error_message

    def __unicode__(self):
        message = (
            json.loads(self.error_message)
            .get('error', {})
            .get('message')
        )
        return u'Status code %s: %s' % (self.status_code, message)

    def __str__(self):
        return unicode(self).decode('utf-8')


def auth_headers(auth_token):
    """Return HTTP authentication headers for API requests.

    Kwargs:
        auth_token: valid API token.

    Returns a dict that can be passed into requests.post as the
        'headers' dict.

    """
    assert auth_token is not None, (
        u"No valid HipChat authentication token found.")
    return {
        'Authorization': 'Bearer %s' % auth_token,
        'Host': 'api.hipchat.com',
        'Content-Type': 'application/json'
    }


def post_json(url, auth_token, payload):
    """POST payload to API.

    Args:
        url: sting, the API endpoint to POST to.
        auth_token: string, a valid API access token.
        payload: dict, the data to post.

    Returns the response object. Raises HipChatError if response code
    is not 2xx.

    """
    resp = requests.post(
        url,
        json=payload,
        headers=auth_headers(auth_token)
    )
    if str(resp.status_code)[:1] != '2':
        raise HipChatError(resp.status_code, resp.text)
    return resp

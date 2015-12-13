# -*- coding: utf-8 -*-
import logging

from hipchat.notifications import send_room_message


class LogHandler(logging.Handler):

    """Log handler used to send notifications to HipChat."""

    DEFAULT_COLOURS = {
        'DEBUG': 'gray',     # background noise
        'INFO': 'yellow',    # default stuff
        'WARNING': 'green',  # used for good things we want to know about
        'ERROR': 'red',      # things we don't like
    }

    def __init__(self, token, room, sender='Django', notify=False,
                 color='yellow', colors=DEFAULT_COLOURS, async=False):
        """
        Initialise log handler.

        Args:
            token: the auth token for access to the API - see hipchat.com
            room: the numerical id of the room to send the message to

        Kwargs:
            sender (optional): the 'from' property of the message - appears in the HipChat window
            notify (optional): if True, HipChat pings / bleeps / flashes when message is received
            color (optional): sets the background color of the message in the HipChat window
            colors (optional): a dict of level:color pairs (e.g. {'DEBUG:'red'} used to
                override the default color)
            async (optional): if True, then writes will be queued using Redis (
                defaults to False.)

        """
        logging.Handler.__init__(self)
        self.token = token
        self.room = room
        self.sender = sender
        self.notify = notify
        self.color = color
        self.colors = colors
        self.async = async
        self.queue = None

    def emit(self, record):
        """Send the record info to HipChat."""
        assert self.token is not None, u"HipChat logger must have a token configured."
        send_room_message(
            self.room,
            record.getMessage(),
            auth_token=self.token,
            color=self.colors.get(record.levelname, self.color),
            sender=self.sender,
            notify=self.notify,
            message_format='html'
        )

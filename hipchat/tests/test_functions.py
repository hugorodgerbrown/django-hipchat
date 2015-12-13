# -*- coding: utf8 -*-
import random

from django.test import TestCase

import mock

import hipchat


def mock_send_room_message(room_id_or_name, message, **kwargs):
    """Fake send_room_message function for testing."""
    message = {
        "room": room_id_or_name,
        "message": message
    }
    message.update(kwargs)
    return message


@mock.patch('hipchat.send_room_message', mock_send_room_message)
class HipChatTests(TestCase):

    """Tests for the core.hipchat functions."""

    def setUp(self):
        """Clear down messages list."""

    def test_yellow(self):
        """Test the yellow function."""

        def _assert_colour(func, message, *args):
            room_id = ''.join(random.sample('qwertyuiopasdfghjklzxcvbnm', 6))
            msg = message % args
            m = func(room_id, message, *args)
            self.assertEqual(m['message'], msg)
            self.assertEqual(m['room'], room_id)

        _assert_colour(hipchat.yellow, 'this is a yellow message: %s', "foo")
        _assert_colour(hipchat.green, 'this is a green message: %s', "bar")
        _assert_colour(hipchat.red, 'this is a red message: %s', "baz")
        _assert_colour(hipchat.purple, 'this is a purple message: %s', 1)
        _assert_colour(hipchat.gray, 'this is a gray message: %s-%s', 1, 2)
        _assert_colour(hipchat.grey, 'this is a grey message%s', None)

    def test_send_user_message(self):
        self.assertRaises(
            AssertionError,
            hipchat.send_user_message,
            None,
            ''
        )

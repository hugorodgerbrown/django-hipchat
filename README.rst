Django HipChat
==============

**Django app for managing custom HipChat add-ons.**

Background
----------

If you're just using the HipChat REST API to send messages (to people) or notifications (to rooms), then this project is not for you - but `this Gist <https://gist.github.com/hugorodgerbrown/89604c5440dc6d82596e>`_ might do the job.

This project is an attempt (WIP) to model the new HipChat Connect platform Add-on structure, so that anyone can set up a new Add-on, with all the bells-and-whistles that come with that - glances, actions, webhooks, etc. It abstracts away the complexity of building up a valid descriptor, automatically generating the callback endpoints. It _should_ allow Django projects to hook into an Add-on simply by importing the project.

.. code:: python

    >>> from hipchat.models import Glance
    >>> g = Glance.objects.get(key="foobar")
    >>> g.update_room("chat", "<b>4</b> open tickets")
    
Underneath the hood there is a back-and-forth between the app and HipChat to ensure that the Add-on has the correction permissions, and that there is a valid API access token that can be used to make API calls.

Status
------

This is a WIP - I have currently managed to get to the point where I have an Add-on that can be installed, that contains a single Glance, that can be updated. There are no webhooks, views, actions or cards.

Usage
-----

Tests
-----

There is a test suite for the app, which is best run through `tox`. If
you wish to run the tests outside of tox, you should install the requirements first:

.. code:: shell

    $ pip install -r requirements.txt
    $ python manage.py test

Licence
-------

MIT

Contributing
------------

Usual rules apply:

1. Fork to your own account
2. Create a branch, fix the issue / add the feature
3. Submit PR

Please take care to follow the coding style - and PEP8.

Acknowledgements
----------------

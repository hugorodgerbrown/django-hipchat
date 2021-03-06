# -*- coding:utf-8 -*-
"""net_promoter_score views."""
import json
import jwt
import logging

from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from hipchat import models
from hipchat import signals

logger = logging.getLogger(__name__)


@require_http_methods(['GET'])
def descriptor(request, app_id):
    """Return the app descriptor JSON to HipChat."""
    app = get_object_or_404(models.Addon, id=app_id)
    return JsonResponse(app.descriptor())


@csrf_exempt
@require_http_methods(['POST'])
def install(request, app_id):
    """Handle the HipChat post-install callback.

    This function creates a new Install object for the app.

    Returns a 201 if the Install is created successfully, else
    a 422 if the Install already exists for the oauth_id sent
    by HipChat (as duplicates aren't allowed).

    """
    app = get_object_or_404(models.Addon, id=app_id)
    data = json.loads(request.body)
    logger.debug("Install data received from HipChat:")
    logger.debug(json.dumps(data, indent=4))
    try:
        install = models.Install(app=app).parse_json(data).save()
        token = install.get_access_token()
        logger.debug("Successful install: %s", install)
        logger.debug("Acquired access token: %s", token)
        return HttpResponse("Thank you for installing our app", status=201)
    except IntegrityError:
        logger.warning("Duplicate HipChat app install oauthId value.")
        return HttpResponse("Thank you for installing our app (again)", status=422)


@csrf_exempt
@require_http_methods(['DELETE'])
def delete(request, app_id, oauth_id):
    """Handle the HipChat post-delete callback.

    This function looks up the Install, and deletes it.

    Returns a 204 if the object is deleted (no content), or
    a 404 if the Install doesn't exist.

    """
    install = get_object_or_404(models.Install, app_id=app_id, oauth_id=oauth_id)
    install.delete()
    return HttpResponse("Sorry to see you go :-(", status=204)


@require_http_methods(['GET'])
def glance(request, glance_id):
    """Return initial glance data for the app.

    If the glance was set up without an explicit external data_url,
    this function is the default endpoint. It uses signals to connect
    to external data - so that a project can import the signal, and
    return a GlanceUpdate object that will be returned to HipChat.

    https://ecosystem.atlassian.net/wiki/display/HIPDEV/HipChat+Glances

    """
    if 'signed_request' not in request.GET:
        return HttpResponseForbidden("Missing signed_request")
    logging.debug('Initial request to load glance: %s', glance_id)
    validate_jwt_token(request)
    glance = get_object_or_404(models.Glance, id=glance_id)
    # this returns a list of 2-tuples (receiver, response)
    data = signals.initialise_glance.send(sender=None, glance=glance)
    # extract out responses that are Updates
    updates = [d[1] for d in data if isinstance(d[1], models.GlanceUpdate)]
    if len(updates) == 0:
        # we received the request, but there's nothing listening,
        # create an empty update
        update = models.GlanceUpdate(
            glance=glance,
            label_value="Briefs",
            lozenge=models.Lozenge(models.LOZENGE_DEFAULT, "Initialising")
        )
    else:
        # return the response from the first signal receiver
        update = updates[0]
    update.save()
    response = JsonResponse(update.content(), status=200)
    response['Access-Control-Allow-Origin'] = '*'
    return response


def validate_jwt_token(request):
    """Validate that the JWT token matches the install.

    Returns a access_token related to the install.

    """
    # code taken from docs:
    # https://ecosystem.atlassian.net/wiki/display/HIPDEV/HipChat+Glances
    jwt_data = request.GET['signed_request']
    try:
        oauth_id = jwt.decode(jwt_data, verify=False)['iss']
        client = models.Install.objects.get(oauth_id=oauth_id)
        data = jwt.decode(jwt_data, client.oauth_secret)
        logger.debug("JWT signed_request data: %s", json.dumps(data, indent=4))
        return client
    except jwt.exceptions.DecodeError:
        logger.exception("Unable to decode JWT token")
        raise Exception()


# ----- experimental ---------------
from django.dispatch import receiver


@receiver(signals.initialise_glance)
def send_initial_data(sender, **kwargs):
    glance = kwargs['glance']
    update = models.GlanceUpdate(
        glance=glance,
        label_value="Briefs",
        lozenge=models.Lozenge(models.LOZENGE_DEFAULT, "Signal received")
    )
    return update

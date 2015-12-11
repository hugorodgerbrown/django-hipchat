# -*- coding:utf-8 -*-
"""net_promoter_score views."""
import json
import logging

from django.contrib.auth.decorators import user_passes_test
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from hipchat.models import HipChatApp, AppInstall, Glance

logger = logging.getLogger(__name__)

@require_http_methods(['GET'])
def descriptor(request, app_id):
    """Return the app descriptor JSON to HipChat."""
    app = get_object_or_404(HipChatApp, id=app_id)
    return JsonResponse(app.descriptor)


@csrf_exempt
@require_http_methods(['POST'])
def install(request, app_id):
    """Handle the HipChat post-install callback.

    This function creates a new AppInstall object for the app.

    Returns a 201 if the AppInstall is created successfully, else
    a 422 if the AppInstall already exists for the oauth_id sent
    by HipChat (as duplicates aren't allowed).

    """
    app = get_object_or_404(HipChatApp, id=app_id)
    data =json.loads(request.body)
    try:
        install = AppInstall(app=app).parse_json(data).save()
        return HttpResponse("Thank you for installing our app", status=201)
    except IntegrityError:
        logger.warning("Duplicate HipChat app install oauthId value.")
        return HttpResponse("Thank you for installing our app (again)", status=422)


@csrf_exempt
@require_http_methods(['DELETE'])
def delete(request, app_id, oauth_id):
    """Handle the HipChat post-delete callback.

    This function looks up the AppInstall, and deletes it.

    Returns a 204 if the object is deleted (no content), or
    a 404 if the AppInstall doesn't exist.

    """
    install = get_object_or_404(AppInstall, app_id=app_id, oauth_id=oauth_id)
    install.delete()
    return HttpResponse("Sorry to see you go :-(", status=204)


@require_http_methods(['GET'])
def glance(request, glance_id):
    """Return initial glance data for the app

    https://ecosystem.atlassian.net/wiki/display/HIPDEV/HipChat+Glances

    """
    glance = get_object_or_404(Glance, id=glance_id)
    data = {
        "label": {
            "type": "html",
            "value": "<b>4</b> Open Briefs"
        },
        "status": {
            "type": "lozenge",
            "value": {
                "label": "LOCKED",
                "type": "current"
            }
        },
        "metadata": {
            "customData": {
                "customAttr": "customValue"
            }
        }
    }
    return JsonResponse(data)

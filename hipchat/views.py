# -*- coding:utf-8 -*-
"""net_promoter_score views."""
import json
import logging

from django.contrib.auth.decorators import user_passes_test
from django.db import IntegrityError
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from hipchat.models import HipChatApp, AppInstall

logger = logging.getLogger(__name__)


def descriptor(request, app_id):
    """Return the app descriptor JSON to HipChat."""
    app = get_object_or_404(HipChatApp, id=app_id)
    return JsonResponse(app.descriptor)

@csrf_exempt
def install(request, app_id):
    """Handle the HipChat post-install callback."""
    app = get_object_or_404(HipChatApp, id=app_id)
    data =json.loads(request.body)
    try:
        install = AppInstall.objects.create_from_install(app, data)
        return HttpResponse("Thank you for installing our app", status=201)
    except IntegrityError:
        logger.warning("Duplicate HipChat app install oauthId value.")
        return HttpResponse("Thank you for installing our app (again)", status=200)


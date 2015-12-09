# -*- coding:utf-8 -*-
"""net_promoter_score views."""
import json

from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.shortcuts import get_object_or_404

from hipchat.models import HipChatApp, AccessToken


def descriptor(request, app_id):
    """Return the app descriptor JSON to HipChat."""
    app = get_object_or_404(HipChatApp, id=app_id)
    return JsonResponse(app.descriptor)


def install(request, app_id):
    """Handle the HipChat post-install callback."""
    app = get_object_or_404(HipChatApp, id=app_id)
    data =json.loads(request.body)
    access_token = AccessToken.objects.parse(data).save()
    return HttpResponse("Thanks for installing our app.")
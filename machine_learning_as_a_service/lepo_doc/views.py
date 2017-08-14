from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse


def get_swagger_json(request, router):
    return JsonResponse(router.api)


def render_docs(request, router, json_url_name):
    return render(request, 'lepo_doc/swagger-ui.html', {
        'json_url': request.build_absolute_uri(reverse(json_url_name)),
    })

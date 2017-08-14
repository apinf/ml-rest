"""machine_learning_as_a_service URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from pkg_resources import resource_filename

from django.conf.urls import include, url
from django.contrib import admin

from lepo.router import Router
from lepo.validate import validate_router
from lepo_doc.urls import get_docs_urls

from data import data_views

router = Router.from_file(resource_filename(__name__, 'machine_learning_as_a_service-openapi_spec_v2.yaml'))
router.add_handlers(data_views)
validate_router(router)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(router.get_urls(), 'api')),
    url(r'^api/', include(get_docs_urls(router, 'api-docs'), 'api-docs')),
]

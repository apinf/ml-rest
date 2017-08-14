from django.conf.urls import url


def get_docs_urls(router, namespace, docs_url='docs/?'):
    from . import views
    json_url_name = 'lepo_doc_%s' % id(router)
    return [
        url('swagger\.json$', views.get_swagger_json, kwargs={'router': router}, name=json_url_name),
        url('%s$' % docs_url, views.render_docs, kwargs={
            'router': router,
            'json_url_name': '%s:%s' % (namespace, json_url_name),
        }),
    ]

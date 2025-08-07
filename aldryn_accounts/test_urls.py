# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, unicode_literals

from django.conf import settings
from django.contrib import admin
from django.urls import re_path
from django.urls import include
from django.urls import i18n_patterns

admin.autodiscover()

urlpatterns = [
    re_path(r'^media/(?P<path>.*)$', 'django.views.static.serve',  # NOQA
        {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    re_path(r'^jsi18n/(?P<packages>\S+?)/$', 'django.views.i18n.javascript_catalog'),  # NOQA
]

urlpatterns += i18n_patterns('',
    re_path(r'^admin/', include(admin.site.urls)),
    re_path(r'^/', include('aldryn_accounts.urls')),
    re_path(r'^', include('cms.urls')),
)



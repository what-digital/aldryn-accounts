# -*- coding: utf-8 -*-
from django.conf import settings
from django.urls import include, path

urlpatterns = []

ALDRYN_ACCOUNTS_ENABLE_PYTHON_SOCIAL_AUTH = getattr(settings, 'ALDRYN_ACCOUNTS_ENABLE_PYTHON_SOCIAL_AUTH', False)
if ALDRYN_ACCOUNTS_ENABLE_PYTHON_SOCIAL_AUTH:
    urlpatterns += [
        path('_psa/', include('social_django.urls', namespace='social'))
    ]

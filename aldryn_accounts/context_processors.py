# -*- coding: utf-8 -*-
from collections import OrderedDict

from django.conf import settings
from django.contrib.auth import get_backends

from social_django.models import UserSocialAuth

from .utils import user_display, get_signup_view, get_login_view
from .notifications import check_notifications


def account_info(request):
    return {
        'username': user_display(request.user),
    }


def social_auth_info(request):
    """
    similar to the social_auth.context_processors.social_auth_by_name_backends,
    but uses a OrderedDict and an easier format to use in templates.
    """
    # TODO: cache (LazyDict does not work well with key value iteration in templates
    backends = get_backends()
    all_keys = set(backends.keys())
    keys = []
    # order backends by setting
    for key in settings.ALDRYN_ACCOUNTS_SOCIAL_BACKEND_ORDERING:
        if key in all_keys:
            keys.append(key)
            all_keys.remove(key)
    for key in all_keys:
        keys.append(key)
    # create accounts dictionary
    accounts = OrderedDict(zip(keys, [None] * len(keys)))
    user = request.user
    if hasattr(user, 'is_authenticated') and user.is_authenticated():
        for assoc in UserSocialAuth.get_social_auth_for_user(user):
            assoc_provider = assoc.provider.replace('-', '_')
            accounts[assoc_provider] = assoc
    return {'social_auth': accounts}


def empty_login_and_signup_forms(request):
    return {
        'empty_login_form': get_login_view().form_class(),
        'empty_signup_form': get_signup_view().form_class(),
    }


def notifications(request):
    if not request.user.is_authenticated:
        return {}
    return {'account_notifications': check_notifications(request.user)}

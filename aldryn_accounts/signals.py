# -*- coding: utf-8 -*-
import django.dispatch
from django.contrib.auth import user_logged_in
from django.db.models import signals, ObjectDoesNotExist
from django.utils.encoding import force_str
from django.utils import timezone
from django.contrib.auth.models import User

from .utils import generate_username


user_signed_up = django.dispatch.Signal()
user_sign_up_attempt = django.dispatch.Signal()
signup_code_sent = django.dispatch.Signal()
signup_code_used = django.dispatch.Signal()
email_confirmed = django.dispatch.Signal()
email_confirmation_sent = django.dispatch.Signal()
password_changed = django.dispatch.Signal()


def set_user_timezone_on_login(sender, user, request, **kwargs):
    try:
        user_settings = user.settings
    except (AttributeError, ObjectDoesNotExist):
        return

    try:
        tz = user_settings.tz
    except AttributeError:
        return

    if tz:
        request.session['django_timezone'] = force_str(tz)
        timezone.activate(tz)

user_logged_in.connect(set_user_timezone_on_login, dispatch_uid='aldryn_accounts:set_user_timezone_on_login')


def set_username_if_not_exists(sender, **kwargs):
    user = kwargs.get('instance')
    if isinstance(user, User):
        if not user.username:
            user.username = generate_username()
signals.pre_save.connect(set_username_if_not_exists, dispatch_uid='aldryn_accounts:generate_username')


# TODO: figure this out. actually we'd need to redirect to a url with the language prefix.
# def set_user_preferred_language_on_login(sender, user, request, **kwargs):
#     from django.db.models import ObjectDoesNotExist
#
#     try:
#         language = user.settings.preferred_language
#         if language and language in dict(settings.LANGUAGES).keys():
#             translation.activate(language)
#     except ObjectDoesNotExist:
#         pass
#
# user_logged_in.connect(set_user_preferred_language_on_login, dispatch_uid='aldryn_accounts:set_user_preferred_language_on_login')

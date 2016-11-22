# -*- coding: utf-8 -*-
from django.contrib.auth import user_logged_in
from django.db.models import signals
from django.utils.encoding import force_text
import django.dispatch


user_signed_up = django.dispatch.Signal(providing_args=["user", "form"])
user_sign_up_attempt = django.dispatch.Signal(providing_args=["username",  "email", "result"])
signup_code_sent = django.dispatch.Signal(providing_args=["signup_code"])
signup_code_used = django.dispatch.Signal(providing_args=["signup_code_result"])
email_confirmed = django.dispatch.Signal(providing_args=["email_address"])
email_confirmation_sent = django.dispatch.Signal(providing_args=["confirmation"])
password_changed = django.dispatch.Signal(providing_args=["user"])


def set_user_timezone_on_login(sender, user, request, **kwargs):
    from django.utils import timezone
    from django.db.models import ObjectDoesNotExist

    try:
        tz = user.settings.timezone
        if tz:
            request.session['django_timezone'] = force_text(tz)
            timezone.activate(tz)
    except ObjectDoesNotExist:
        pass

user_logged_in.connect(set_user_timezone_on_login, dispatch_uid='aldryn_accounts:set_user_timezone_on_login')


def generate_username(sender, **kwargs):
    from django.contrib.auth.models import User
    import uuid
    user = kwargs.get('instance')
    if isinstance(user, User):
        if not user.username:
            user.username = uuid.uuid4().get_hex()[:30]
signals.pre_save.connect(generate_username, dispatch_uid='aldryn_accounts:generate_username')


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

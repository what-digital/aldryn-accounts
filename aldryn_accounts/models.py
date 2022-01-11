# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import operator

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode  # Python 2

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

import timezone_field
from annoying.fields import AutoOneToOneField
from six.moves import reduce

from .conf import settings
from .exceptions import EmailAlreadyVerified, VerificationKeyExpired
from .signals import signup_code_used, signup_code_sent, email_confirmed, email_confirmation_sent
from .utils import profile_image_upload_to, random_token
from .monkeypatches import patch_user_unicode
from .emails import EmailSender

patch_user_unicode()


class SignupCode(models.Model):

    class AlreadyExists(Exception):
        pass

    class InvalidCode(Exception):
        pass

    code = models.CharField(max_length=64, unique=True)
    max_uses = models.PositiveIntegerField(default=0)
    expires_at = models.DateTimeField(null=True, blank=True)
    invited_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL
    )
    email = models.EmailField(blank=True)
    notes = models.TextField(blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    use_count = models.PositiveIntegerField(editable=False, default=0)

    def __str__(self):
        if self.email:
            return "%s [%s]" % (self.email, self.code)
        else:
            return self.code

    @classmethod
    def exists(cls, code=None, email=None):
        checks = []
        if code:
            checks.append(models.Q(code=code))
        if email:
            checks.append(models.Q(email=email))
        return cls._default_manager.filter(reduce(operator.or_, checks)).exists()

    @classmethod
    def create(cls, **kwargs):
        email, code = kwargs.get("email"), kwargs.get("code")
        expires_at = timezone.now() + datetime.timedelta(hours=kwargs.get("expires_at", 24))
        if not code:
            code = random_token([email]) if email else random_token()

        if kwargs.get("check_exists", True) and cls.exists(code=code, email=email):
            raise cls.AlreadyExists()
        params = {
            "code": code,
            "max_uses": kwargs.get("max_uses", 0),
            "expires_at": expires_at,
            "invited_by": kwargs.get("invited_by"),
            "notes": kwargs.get("notes", "")
        }
        if email:
            params["email"] = email
        return cls(**params)

    def is_valid(self):
        """
        Check if code is valid. Returns True or False.
        """
        if self.max_uses and self.max_uses <= self.use_count:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True

    def calculate_use_count(self):
        self.use_count = self.signupcoderesult_set.count()
        self.save()

    def use(self, user):
        """
        Add a SignupCode result attached to the given user.
        """
        result = SignupCodeResult()
        result.signup_code = self
        result.user = user
        result.save()
        signup_code_used.send(sender=result.__class__, signup_code_result=result)

    def send(self, **kwargs):
        EmailSender.send_signup_code(**kwargs)
        signup_code_sent.send(
            sender=self.__class__,
            signup_code=self,
        )


class SignupCodeResult(models.Model):

    signup_code = models.ForeignKey(SignupCode, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(default=timezone.now)

    def save(self, **kwargs):
        super(SignupCodeResult, self).save(**kwargs)
        self.signup_code.calculate_use_count()


class EmailAddressManager(models.Manager):

    def add_email(self, user, email, make_primary=False, **kwargs):
        is_first_email = user and email and not self.filter(user=user).exists()
        email_address, created = self.get_or_create(user=user, email=email, defaults=kwargs)
        if not created:
            for key, value in kwargs.items():
                setattr(email_address, key, value)
            email_address.save()
        if is_first_email or make_primary:
            email_address.set_as_primary()
        return email_address

    def get_primary(self, user):
        try:
            return self.get(user=user, is_primary=True)
        except self.model.DoesNotExist:
            return None

    def get_for_user(self, user):
        """
        Returns a queryset of EmailAddress objects for a given user.
        """
        return self.filter(user=user)

    def get_user_for(self, email):
        return self.get(email=email)

    def has_verified_email(self, user):
        return self.filter(user=user).exists()


class EmailAddress(models.Model):
    """
    All verified email addresses. If it's not verified it should not be here.
    """
    is_verified = True
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_method = models.CharField(max_length=255, blank=True, default='unknown')
    is_primary = models.BooleanField(default=False)

    objects = EmailAddressManager()

    class Meta:
        verbose_name = _("E-Mail address")
        verbose_name_plural = _("E-Mail addresses")

    def clean(self):
        self.email = self.email.strip().lower()

    def __str__(self):
        return "%s (%s)" % (self.email, self.user)

    def set_as_primary(self, commit=True):
        old_primary = EmailAddress.objects.get_primary(self.user)
        if old_primary:
            old_primary.is_primary = False
            if commit:
                old_primary.save()
        self.is_primary = True
        if commit:
            self.save()
        self.user.email = self.email
        if commit:
            self.user.save()
        return True

    def save(self, *args, **kwargs):
        user_needs_save = False
        if self.is_primary:
            if not self.user.email == self.email:
                self.set_as_primary(commit=False)
                user_needs_save = True
        result = super(EmailAddress, self).save(*args, **kwargs)
        if user_needs_save:
            self.user.save()
        return result


class EmailConfirmationManager(models.Manager):
    def delete_expired_confirmations(self):
        for confirmation in self.all().exclude(sent_at__isnull=True):
            if confirmation.key_expired():
                confirmation.delete()

    def request(self, user, email, is_primary=False, send=False):
        key = random_token([email])
        email_confirmation = self.create(user=user, email=email, key=key, is_primary=is_primary)
        if not user.email:  #
            user.email = email
            user.save()
        if send:
            email_confirmation.send()
        return email_confirmation


class EmailConfirmation(models.Model):
    user = models.ForeignKey(
        User, related_name="email_verifications", on_delete=models.CASCADE
    )
    email = models.EmailField()
    is_primary = models.BooleanField(default=True)
    # TODO: rename this to EmailVerification
    created_at = models.DateTimeField(default=timezone.now)
    sent_at = models.DateTimeField(null=True)
    key = models.CharField(max_length=64, unique=True)

    objects = EmailConfirmationManager()

    class Meta:
        verbose_name = _("E-Mail confirmation")
        verbose_name_plural = _("E-Mail confirmations")

    def __str__(self):
        return "confirmation for %s (%s)" % (self.email, self.user)

    def clean(self):
        self.email = self.email.strip().lower()

    def key_expired(self):
        expire_days = getattr(
            settings, 'ALDRYN_ACCOUNTS_EMAIL_CONFIRMATION_EXPIRE_DAYS', 5)
        expiration_date = self.sent_at + datetime.timedelta(days=expire_days)
        return expiration_date <= timezone.now()
    key_expired.boolean = True

    def confirm(self, verification_method='unknown', delete=True):
        if self.sent_at and not self.key_expired():
            if EmailAddress.objects.filter(email=self.email).exists():
                raise EmailAlreadyVerified("%s already exists" % self.email)
            data = dict(
                verified_at=timezone.now(),
                verification_method=verification_method,
            )
            email_address = EmailAddress.objects.add_email(
                user=self.user, email=self.email, make_primary=self.is_primary, **data)
            email_confirmed.send(sender=self.__class__, email_address=email_address)
            if delete:
                EmailConfirmation.objects.filter(email=self.email).delete()
            return email_address
        else:
            msg = _("Verification key {key} for {email} has been expired").format(
                    key=self.key, email=self.email)
            raise VerificationKeyExpired(msg)

    def send(self, **kwargs):
        kwargs['verification'] = self
        EmailSender.send_email_verification(**kwargs)
        email_confirmation_sent.send(
            sender=self.__class__,
            confirmation=self,
        )


class UserSettings(models.Model):
    user = AutoOneToOneField(User, related_name='settings', unique=True, db_index=True, on_delete=models.CASCADE)
    birth_date = models.DateField(_('birth date'), blank=True, null=True)
    timezone = timezone_field.TimeZoneField(blank=True, null=True, default=None, verbose_name=_('time zone'))

    location_name = models.CharField(_('location'), blank=True, default='', max_length=255)
    location_latitude = models.FloatField(null=True, blank=True, default=None)
    location_longitude = models.FloatField(null=True, blank=True, default=None)

    profile_image = models.ImageField(verbose_name=_('profile image'), blank=True, default='', max_length=255,
                                      upload_to=profile_image_upload_to)
    preferred_language = models.CharField(_('language'), blank=True, default='', choices=settings.LANGUAGES, max_length=32)

    class Meta:
        verbose_name = _('user settings')
        verbose_name_plural = _('user settings')

    def __str__(self):
        return '{0} ({1})'.format(self.user.username, self.user.pk)

# South rules
rules = [
    (
        (AutoOneToOneField,),
        [],
        {
            "to": ["rel.to", {}],
            "to_field": ["rel.field_name", {"default_attr": "rel.to._meta.pk.name"}],
            "related_name": ["rel.related_name", {"default": None}],
            "db_index": ["db_index", {"default": True}],
        },
    )
]
try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules(rules, ["^annoying\.fields\.AutoOneToOneField"])
except ImportError:
    # no south, Django version >1.6
    pass

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from distutils.version import LooseVersion
from cms import __version__ as cms_string_version

cms_version = LooseVersion(cms_string_version)


def noop_gettext(s):
    return s

gettext = noop_gettext


HELPER_SETTINGS = {
    # plug urls directly, test_urls includes urls from djangocms-helper
    'ROOT_URLCONF': 'aldryn_accounts.test_urls',
    'TIME_ZONE': 'UTC',
    'INSTALLED_APPS': [
        'aldryn_common',
        'easy_thumbnails',
        'reversion',
        'djangocms_text_ckeditor',
        'standard_form',
        'aldryn_accounts',
        'absolute',
    ],
    'CMS_PERMISSION': True,
    'LANGUAGES': (
        ('en', 'English'),
        ('de', 'German'),
    ),
    'CMS_LANGUAGES': {
        'default': {
            'public': True,
            'hide_untranslated': False,
            'fallbacks': ['en']

        },
        1: [
            {
                'public': True,
                'code': 'en',
                'fallbacks': [u'de'],
                'hide_untranslated': False,
                'name': gettext('en'),
                'redirect_on_fallback': True,
            },
            {
                'public': True,
                'code': 'de',
                'fallbacks': [u'en'],
                'hide_untranslated': False,
                'name': gettext('de'),
                'redirect_on_fallback': True,
            },
        ],
    },
    'EMAIL_BACKEND': 'django.core.mail.backends.locmem.EmailBackend',
    'DEBUG': True,
    # 'TEMPLATE_DEBUG': True,
    'CACHES': {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    },
    # until session engine is hardcoded in djangocms-helper use
    # @override_settings in your test cases.
    'SESSION_ENGINE': 'django.contrib.sessions.backends.cached_db',
    'MIDDLEWARE': [
        # NOTE: This will actually be removed below in CMS<3.2 installs.
        'cms.middleware.utils.ApphookReloadMiddleware',
        'django.middleware.http.ConditionalGetMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.middleware.locale.LocaleMiddleware',
        'django.middleware.common.CommonMiddleware',
        'cms.middleware.language.LanguageCookieMiddleware',
        'cms.middleware.user.CurrentUserMiddleware',
        'cms.middleware.page.CurrentPageMiddleware',
        'cms.middleware.toolbar.ToolbarMiddleware'
    ],
    'THUMBNAIL_PROCESSORS': (
        'easy_thumbnails.processors.colorspace',
        'easy_thumbnails.processors.autocrop',
        # since we don't have filer in dependencies - but we use upscale
        # we need at least one processor which processes upscale
        # if filer is in the dependencies - please use
        # 'filer.thumbnail_processors.scale_and_crop_with_subject_location',
        'easy_thumbnails.processors.scale_and_crop',
        'easy_thumbnails.processors.filters',
    ),
    # aldryn-accounts related
    'ALDRYN_ACCOUNTS_USE_PROFILE_APPHOOKS': True,
}

# If using CMS 3.2+, use the CMS middleware for ApphookReloading, otherwise,
# use aldryn_apphook_reload's.
if cms_version < LooseVersion('3.2.0'):
    HELPER_SETTINGS['INSTALLED_APPS'].insert(0, 'aldryn_apphook_reload')
    HELPER_SETTINGS['MIDDLEWARE'].remove(
        'cms.middleware.utils.ApphookReloadMiddleware')
    HELPER_SETTINGS['MIDDLEWARE'].insert(
        0, 'aldryn_apphook_reload.middleware.ApphookReloadMiddleware')


def run():
    from djangocms_helper import runner
    runner.cms('aldryn_accounts', extra_args=[])

if __name__ == "__main__":
    run()

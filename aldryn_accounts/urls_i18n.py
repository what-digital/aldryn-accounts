# -*- coding: utf-8 -*-
from django.conf import settings
from django.urls import re_path, include

from . import views, utils


accounts_urlpatterns = [
    re_path(r'^signup/$', utils.get_signup_view().as_view(), name='accounts_signup'),
    re_path(r'^signup/email/resend-confirmation/$', views.SignupEmailResendConfirmationView.as_view(), name='accounts_signup_email_resend_confirmation'),
    re_path(r'^signup/email/confirmation-sent/$', views.SignupEmailConfirmationSentView.as_view(), name='accounts_signup_email_confirmation_sent'),
    re_path(r'^signup/email/sent/$', views.SignupEmailSentView.as_view(), name='accounts_signup_email_sent'),

    re_path(r'^login/$', utils.get_login_view().as_view(), name='login'),
    re_path(r'^logout/$', views.LogoutView.as_view(), name='logout'),

    re_path(r'^password-reset/$', views.password_reset, name='accounts_password_reset_recover'),  # new name should be password_reset
    re_path(r'^password-reset/sent/$', views.password_reset_done, name='password_reset_done'),
    re_path(r'^password-reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.password_reset_confirm, name='password_reset_confirm'),
    re_path(r'^password-reset/done/$', views.password_reset_complete, name='password_reset_complete'),

    re_path(r'^email/confirm/(?P<key>\w+)/$', views.ConfirmEmailView.as_view(), name='accounts_confirm_email'),
]


profile_index_urlpatterns = [
    re_path(r'^$', views.ProfileView.as_view(), name='accounts_profile'),
]


profile_settings_urlpatterns = [
    re_path(r'^$', views.UserSettingsView.as_view(), name='accounts_settings')
]


associations_urlpatterns = [
    re_path(r'^$', views.ProfileAssociationsView.as_view(), name='accounts_profile_associations'),
]


change_password_urlpatterns = [
    re_path(r'^$', views.ChangePasswordView.as_view(), name='accounts_change_password'),
    re_path(r'^create/$', views.CreatePasswordView.as_view(), name='accounts_create_password'),
]


email_settings_urlpatterns = [
    re_path(r'^$', views.ProfileEmailListView.as_view(), name='accounts_email_list'),
    re_path(r'^confirmation/(?P<pk>\d+)/re-send/$', views.ProfileEmailConfirmationResendView.as_view(), name='accounts_email_confirmation_resend'),
    re_path(r'^confirmation/(?P<pk>\d+)/cancel/$', views.ProfileEmailConfirmationCancelView.as_view(), name='accounts_email_confirmation_cancel'),
    re_path(r'^(?P<pk>\d+)/delete/$', views.ProfileEmailDeleteView.as_view(), name='accounts_email_delete'),
    re_path(r'^(?P<pk>\d+)/make_primary/$', views.ProfileEmailMakePrimaryView.as_view(), name='accounts_email_make_primary'),
]

ALDRYN_ACCOUNTS_USE_PROFILE_APPHOOKS = getattr(settings, 'ALDRYN_ACCOUNTS_USE_PROFILE_APPHOOKS', False)
if not ALDRYN_ACCOUNTS_USE_PROFILE_APPHOOKS:
    accounts_urlpatterns += [
        re_path(r'^profile/settings/', include(profile_settings_urlpatterns)),
        re_path(r'^profile/associations/', include(associations_urlpatterns)),
        re_path(r'^profile/password/', include(change_password_urlpatterns)),
        re_path(r'^profile/email/', include(email_settings_urlpatterns)),
        re_path(r'^profile/', include(profile_index_urlpatterns)),
    ]

prefix = getattr(settings, 'ALDRYN_ACCOUNTS_URLS_PREFIX', '')
prefix = '{}/'.format(prefix) if prefix else ''

urlpatterns = [
    re_path(r'^{}'.format(prefix), include(accounts_urlpatterns, namespace='aldryn_accounts'))
]

# -*- coding: utf-8 -*-
from django.utils import timezone
from django.conf import settings

from pytz import UnknownTimeZoneError

from .utils import geoip


class TimezoneMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_request(self, request):
        tz = request.session.get('django_timezone')
        if tz:
            try:
                timezone.activate(tz)
            except UnknownTimeZoneError:
                tz = settings.TIME_ZONE
                request.session['django_timezone'] = tz
                timezone.activate(tz)


class GeoIPMiddleware(object):
    """
    Still experimental
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_request(self, request):
        ip = request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR') or None
        # ip = '67.2.2.25'
        # ip = '99.27.181.216'  # LA
        # ip = '92.104.226.167'  # Switzerland (Stefan Home)
        # ip = '213.189.154.40'  # Switzerland (Divio)
        data = geoip(ip)
        if data is not None:
            request.session['geoip'] = data
            if not request.session.get('django_timezone') and data.get('time_zone'):
                request.session['django_timezone'] = data.get('time_zone')
            if (not (request.session.get('django_location') or request.session.get('django_location_name'))
                    and data.get('pretty_name') and data.get('latitude') and data.get('longitude') or True):
                request.session['django_location'] = (data.get('latitude'), data.get('longitude'),)
                request.session['django_location_name'] = data.get('pretty_name')

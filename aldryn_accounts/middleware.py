# -*- coding: utf-8 -*-
from django.utils import timezone
from django.conf import settings

from pytz import UnknownTimeZoneError

from .utils import geoip


class TimezoneMiddleware(object):
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        if self.get_response:
            response = self.get_response(request)
            return response

    def process_request(self, request):
        try:
            tz = request.session.get('django_timezone')
            if tz:
                try:
                    timezone.activate(tz)
                except UnknownTimeZoneError:
                    tz = settings.TIME_ZONE
                    request.session['django_timezone'] = tz
                    timezone.activate(tz)
        except (KeyError, AttributeError):
            # Handle cases where session is not properly initialized
            pass


class GeoIPMiddleware(object):
    """
    Still experimental
    """
    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        self.process_request(request)
        if self.get_response:
            response = self.get_response(request)
            return response

    def process_request(self, request):
        try:
            # Skip GeoIP lookup during signup if configured to do so
            from .conf import settings
            if (settings.ALDRYN_ACCOUNTS_SKIP_GEOIP_ON_SIGNUP and 
                request.path_info and 'signup' in request.path_info):
                return
                
            ip = request.META.get('HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR') or None
            # ip = '67.2.2.25'
            # ip = '99.27.181.216'  # LA
            # ip = '92.104.226.167'  # Switzerland (Stefan Home)
            # ip = '213.189.154.40'  # Switzerland (Divio)
            
            # Skip GeoIP lookup if no IP is available
            if not ip:
                return
                
            data = geoip(ip)
            if data is not None and data:  # Check for non-empty dict
                request.session['geoip'] = data
                if not request.session.get('django_timezone') and data.get('time_zone'):
                    request.session['django_timezone'] = data.get('time_zone')
                if (not (request.session.get('django_location') or request.session.get('django_location_name'))
                        and data.get('pretty_name') and data.get('latitude') and data.get('longitude')):
                    request.session['django_location'] = (data.get('latitude'), data.get('longitude'),)
                    request.session['django_location_name'] = data.get('pretty_name')
        except (KeyError, AttributeError, Exception) as e:
            # Handle cases where session is not properly initialized or GeoIP fails
            # Log the error but don't let it break the request
            import logging
            logger = logging.getLogger('aldryn_accounts.middleware')
            logger.warning("GeoIP middleware failed: %s", str(e))
            pass

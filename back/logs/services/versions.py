import datetime
import django
import rest_framework
import OpenSSL
import ssl
import urllib.request
from platform import python_version
from django.conf import settings
# from core.mysql_ver import get_mysql_ver

class VersionsLogData():
    template_name = 'versions'

    def get_extra_context(self, request):
        context = {}
        context['python_version'] = python_version()
        context['django_version'] = '{}.{}.{} {}'.format(*django.VERSION)
        context['drf_version'] = '{}'.format(rest_framework.VERSION)
        host = settings.DJANGO_HOST
        api_host = settings.DJANGO_HOST_API
        if host != 'localhost':
            ssl_context = ssl._create_unverified_context()
            response = urllib.request.urlopen(api_host, context=ssl_context)
            versions = response.headers['Server'].split(' ')
            for ver in versions:
                if 'Apache' in ver:
                    context['apache_version'] = ver.split('/')[1]
                if 'OpenSSL' in ver:
                    context['openssl_version'] = ver.split('/')[1]
                if 'mod_wsgi' in ver:
                    context['mod_wsgi_version'] = ver.split('/')[1]
        context['hmail_version'] = '5.6.7 bld 2425'
        # context['mysql_version'] = get_mysql_ver()
        context['izitoast_version'] = get_izitoast_ver()
        context['swiper_version'] = get_swiper_ver()
        context['firebase_version'] = get_firebase_ver()

        try:
            cert = ssl.get_server_certificate((settings.DOMAIN_NAME, 443))
            x509 = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, cert)
            t = x509.get_notAfter()
            d = datetime.date(int(t[0:4]),int(t[4:6]),int(t[6:8]))
            context['cert_termin'] = d.strftime('%d.%m.%Y')
        except:
            pass
        return context


def get_izitoast_ver():
    return '1.4.0'

def get_swiper_ver():
    return '8.4.5'

def get_firebase_ver():
    return '7.16.1'


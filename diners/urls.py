from django.conf import settings
from django.conf.urls import url

from diners import views


app_name = 'diners'

urlpatterns = [
    # Diners pin
    url(r'^diners/rfid/$', views.RFID, name='rfid'),
    url(r'^diners/$', views.diners, name='diners'),
    url(r'^diners/logs/$', views.diners_logs, name='diners_logs'),
    url(r'^diners/satisfaction-rating/$', views.satisfaction_rating, name='satisfaction_rating'),
    url(r'^diners/analytics/$', views.analytics, name='analytics'),
]

# Test
if settings.DEBUG:
    urlpatterns.append( url(r'^diners/test/$', views.test, name='diners_test'))
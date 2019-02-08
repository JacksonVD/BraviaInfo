from django.urls import path
from . import views

urlpatterns = [
    # The various views to run when redirecting to pages
    path('', views.home, name='home'),
    path('power_change', views.setPower, name='power_change'),
    path('vol_change', views.setVolume, name='vol_change'),
    path('source_select', views.setSource, name='source_select'),
    path('app_select', views.setApp, name='app_select'),
    path('send_ircc', views.sendIRCC, name='send_ircc'),
    path('tvinfo', views.getInfo, name='tvinfo'),
    path('send_keyboard', views.sendKeyboard, name='send_keyboard'),
]

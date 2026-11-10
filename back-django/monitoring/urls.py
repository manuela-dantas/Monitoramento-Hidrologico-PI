from django.urls import path, re_path

from . import views

urlpatterns = [
    path('health', views.health),
    path('stations', views.stations),
    path('stations/<str:station_id>/summary', views.station_summary),
    path('stations/<str:station_id>/series', views.station_series),
    re_path(r'^(?P<unknown_path>.*)$', views.not_found),
]
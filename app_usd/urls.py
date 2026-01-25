from django.urls import path

from . import views

urlpatterns = [
    path("get-current-usd/", views.get_usd_rate, name="get_usd"),
    path("currency/<str:currency_code>/", views.get_currency_rate, name="get_currency"),
    path("currencies/", views.get_available_currencies, name="available_currencies"),
]

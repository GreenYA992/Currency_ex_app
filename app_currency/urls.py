from django.urls import path

from . import views

urlpatterns = [
    path(
        "get-current-<str:currency_code>/",
        views.get_currency_rate,
        name="get_<currency>",
    ),
    # path("currency/<str:currency_code>/", views.get_currency_rate, name="get_currency"),
    path(
        "currencies/",
        views.get_available_currencies,
        name="available_currencies",
    ),
]

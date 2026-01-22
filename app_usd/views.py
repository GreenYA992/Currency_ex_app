from django.http import JsonResponse
from .models import ExchangeRate
from .services.exchange import ExchangeService

class FormatJsonResponse(JsonResponse):
    def __init__(self, data, **kwargs):
        kwargs.setdefault("json_dumps_params",{
            "indent": 2,
            "ensure_ascii": False,
            "sort_keys": True
        })
        super().__init__(data, **kwargs)

def get_current_usd(request):
    try:
        current_rate = ExchangeService.get_usd_rate()
        status = "success"
    except Exception as e:
        current_rate = None
        status = str(e)

    last_rates = ExchangeRate.objects.all()[:10].values("rate", "timestamp")

    return FormatJsonResponse({
        "status": status,
        "current_rate": current_rate,
        "last_rates": list(last_rates.values("rate", "timestamp"))
    })

def raw_material_stock_alert(request):
    if not hasattr(request, "session"):
        return {}

    alerts = request.session.pop("raw_material_stock_alerts", [])
    return {"raw_material_stock_alerts": alerts}


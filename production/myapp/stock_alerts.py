from .models import RawMaterial


RAW_MATERIAL_ALERT_DAYS = 10


def get_low_raw_material_alerts():
    alerts = []
    materials = RawMaterial.objects.filter(
        is_active=True,
        one_day_requirement__gt=0,
    ).order_by("category", "name")

    for material in materials:
        current_stock = float(material.current_stock or 0)
        one_day = float(material.one_day_requirement or 0)
        required_stock = one_day * RAW_MATERIAL_ALERT_DAYS

        if current_stock < required_stock:
            days_left = current_stock / one_day if one_day else 0
            alerts.append({
                "name": material.name,
                "category": material.category,
                "current_stock": round(current_stock, 2),
                "one_day_requirement": round(one_day, 2),
                "required_stock": round(required_stock, 2),
                "days_left": round(days_left, 1),
            })

    return alerts


def queue_low_raw_material_alert(request):
    alerts = get_low_raw_material_alerts()
    if alerts:
        request.session["raw_material_stock_alerts"] = alerts
    else:
        request.session.pop("raw_material_stock_alerts", None)


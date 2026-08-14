"""
Power BI Report Data Generators
Provides report-specific data for each module type
"""

from django.db.models import Sum, Count, Avg, F, Q, FloatField, IntegerField, Value, Case, When
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json
from collections import defaultdict

from .models import (
    Production, Planning, Formulation, FormulationItem, Stock, RawMaterial,
    RawMaterialStock, DeliveryChallan, ScrapLog, WeightSheet, WeightSheetRow,
    UnfinishedProduction, Machine, CustomUser
)


def _get_report_type(request):
    """Extract report type from request"""
    return request.GET.get("report_type", "production")


def _apply_date_filter(queryset, from_date, to_date, date_field="created_at__date"):
    """Apply date range filter if dates provided"""
    if from_date and to_date:
        try:
            queryset = queryset.filter(**{f"{date_field}__range": [from_date, to_date]})
        except Exception:
            pass
    return queryset


def _apply_machine_filter(queryset, machine_ids):
    """Apply machine filter if provided"""
    if machine_ids:
        queryset = queryset.filter(machine_id__in=machine_ids)
    return queryset


def _apply_operator_role_filter(queryset, user):
    """Filter by operator role"""
    if hasattr(user, 'role') and user.role == 'Operator':
        queryset = queryset.filter(operator=user)
    return queryset


def _apply_operator_role_filter_scrap(queryset, user):
    """Filter scrap by operator role"""
    if hasattr(user, 'role') and user.role == 'Operator':
        queryset = queryset.filter(production__operator=user)
    return queryset


def _apply_machine_filter_scraps(queryset, machine_ids):
    """Apply machine filter for scrap queryset"""
    if machine_ids:
        queryset = queryset.filter(production__machine_id__in=machine_ids)
    return queryset


def _get_production_data(request, prods, from_date, to_date):
    """Generate data for Production reports"""
    # KPIs
    total_qty = prods.aggregate(s=Sum('quantity'))['s'] or 0
    total_weight = prods.aggregate(s=Sum(F('quantity') * F('weight_per_piece')))['s'] or 0
    pending_count = prods.filter(status='Pending').count()

    today = timezone.now().date()
    today_prods = prods.filter(created_at__date=today)
    today_qty = today_prods.aggregate(s=Sum('quantity'))['s'] or 0
    today_weight = today_prods.aggregate(s=Sum(F('quantity') * F('weight_per_piece')))['s'] or 0

    top_machine_today = today_prods.values('machine__name').annotate(
        total=Sum(F('quantity') * F('weight_per_piece'))
    ).order_by('-total').first()
    top_machine_name = top_machine_today['machine__name'] if top_machine_today else "-"

    total_machines = Machine.objects.filter(is_active=True).count()
    active_machines_today = today_prods.values('machine').distinct().count()
    utilization = round((active_machines_today / total_machines * 100), 1) if total_machines else 0

    # Trend data
    trend_data = prods.values('created_at__date').annotate(
        total_qty=Sum('quantity'),
        total_weight=Sum(F('quantity') * F('weight_per_piece'))
    ).order_by('created_at__date')
    trend_labels = [str(d['created_at__date']) for d in trend_data]
    trend_qty = [float(d['total_qty'] or 0) for d in trend_data]
    trend_weight = [float(d['total_weight'] or 0) for d in trend_data]

    # Category data
    cat_data = prods.values('category').annotate(
        total_qty=Sum('quantity'),
        total_weight=Sum(F('quantity') * F('weight_per_piece'))
    )
    cat_labels = [d['category'] for d in cat_data]
    cat_values = [float(d['total_weight'] or 0) for d in cat_data]

    # Machine data
    machine_data = prods.values('machine__name').annotate(
        total_qty=Sum('quantity'),
        total_weight=Sum(F('quantity') * F('weight_per_piece'))
    ).order_by('-total_weight')[:10]
    machine_labels = [d['machine__name'] for d in machine_data]
    machine_values = [float(d['total_weight'] or 0) for d in machine_data]

    # Shift data
    shift_data = prods.values('shift').annotate(
        total_qty=Sum('quantity'),
        total_weight=Sum(F('quantity') * F('weight_per_piece'))
    )
    day_weight = sum(float(d['total_weight'] or 0) for d in shift_data if d['shift'] == 'Day')
    night_weight = sum(float(d['total_weight'] or 0) for d in shift_data if d['shift'] == 'Night')
    day_qty = sum(float(d['total_qty'] or 0) for d in shift_data if d['shift'] == 'Day')
    night_qty = sum(float(d['total_qty'] or 0) for d in shift_data if d['shift'] == 'Night')

    # Operator data
    operator_data = prods.values('operator__full_name').annotate(
        total_qty=Sum('quantity'),
        total_weight=Sum(F('quantity') * F('weight_per_piece'))
    ).order_by('-total_weight')[:10]
    operator_labels = [d['operator__full_name'] or '-' for d in operator_data]
    operator_values = [float(d['total_weight'] or 0) for d in operator_data]

    # Scrap data
    scrap_data = prods.aggregate(
        total_sidepatti=Sum('sidepatti'),
        total_linesetting=Sum('linesetting'),
        total_rejected=Sum('rejected_quantity')
    )
    scrap_sidepatti = float(scrap_data['total_sidepatti'] or 0)
    scrap_linesetting = float(scrap_data['total_linesetting'] or 0)
    scrap_rejected = float(scrap_data['total_rejected'] or 0)

    # Table data
    table_data = []
    for p in prods.order_by('-created_at')[:200]:
        table_data.append({
            'date': p.created_at.strftime('%d %b %Y'),
            'machine': p.machine.name if p.machine else '-',
            'operator': p.operator.full_name if p.operator else '-',
            'shift': p.shift,
            'category': p.category,
            'product': p.product.product_name if p.product else '-',
            'qty': p.quantity,
            'weight': round(float(p.quantity) * float(p.weight_per_piece), 2),
            'sidepatti': float(p.sidepatti or 0),
            'linesetting': float(p.linesetting or 0),
            'status': p.status,
            'rejected': float(p.rejected_quantity or 0),
        })

    # Pivot data
    pivot_data = []
    for p in prods.order_by('-created_at')[:500]:
        pivot_data.append({
            'Date': p.created_at.strftime('%Y-%m-%d'),
            'Machine': p.machine.name if p.machine else '-',
            'Operator': p.operator.full_name if p.operator else '-',
            'Shift': p.shift,
            'Category': p.category,
            'Product': p.product.product_name if p.product else '-',
            'Quantity': p.quantity,
            'Weight': round(float(p.quantity) * float(p.weight_per_piece), 2),
            'Side Patti': float(p.sidepatti or 0),
            'Line Setting': float(p.linesetting or 0),
            'Status': p.status,
            'Rejected': float(p.rejected_quantity or 0),
        })

    kpis = {
        'total_qty': total_qty,
        'total_weight': round(float(total_weight), 2),
        'today_qty': today_qty,
        'today_weight': round(float(today_weight), 2),
        'pending': pending_count,
        'utilization': utilization,
        'top_machine': top_machine_name,
    }

    charts = {
        'trend': {'labels': trend_labels, 'qty': trend_qty, 'weight': trend_weight},
        'category': {'labels': cat_labels, 'values': cat_values},
        'machine': {'labels': machine_labels, 'values': machine_values},
        'shift': {'day_qty': day_qty, 'night_qty': night_qty, 'day_weight': day_weight, 'night_weight': night_weight},
        'operator': {'labels': operator_labels, 'values': operator_values},
        'scrap': {'sidepatti': scrap_sidepatti, 'linesetting': scrap_linesetting, 'rejected': scrap_rejected},
    }

    table_config = {
        'headers': ['#', 'Date', 'Machine', 'Operator', 'Shift', 'Category', 'Product',
                    'Qty', 'Weight', 'Side Patti', 'Line Setting', 'Rejected', 'Status'],
        'keys': ['date', 'machine', 'operator', 'shift', 'category', 'product',
                 'qty', 'weight', 'sidepatti', 'linesetting', 'rejected', 'status']
    }

    pivot_config = {
        'rows': ['Machine', 'Date', 'Operator', 'Category', 'Shift'],
        'cols': ['Shift', 'Category', 'Machine', 'Status'],
        'values': ['Quantity', 'Weight', 'Side Patti', 'Line Setting', 'Rejected'],
        'agg': ['sum', 'avg', 'count', 'min', 'max']
    }

    return {
        'kpis': kpis,
        'charts': charts,
        'table_data': table_data,
        'table_config': table_config,
        'pivot_data': pivot_data,
        'pivot_config': pivot_config,
    }


def _get_planning_data(request, from_date, to_date, machine_ids, category):
    """Generate detailed data for Planning reports"""
    plans = Planning.objects.all().select_related('machine', 'thickness', 'height', 'width', 'density', 'color')

    if hasattr(request, 'user') and hasattr(request.user, 'role') and request.user.role == 'Operator':
        plans = plans.filter(machine__machineoperator__operator=request.user).distinct()

    if from_date and to_date:
        try:
            plans = plans.filter(date__range=[from_date, to_date])
        except Exception:
            pass

    if machine_ids:
        plans = plans.filter(machine_id__in=machine_ids)
    if category:
        plans = plans.filter(category=category)

    # Calculate actual production from planning
    plan_ids = list(plans.values_list('id', flat=True))
    actual_data = Production.objects.filter(planning_id__in=plan_ids).values('planning').annotate(
        actual_qty=Sum('quantity')
    )
    actual_map = {item['planning']: item['actual_qty'] for item in actual_data}

    # KPIs
    total_planned = plans.aggregate(s=Sum('quantity'))['s'] or 0
    total_actual = sum(actual_map.values())
    pending_plans = plans.filter(quantity__gt=0).count()
    completion_rate = round((total_actual / total_planned * 100), 1) if total_planned else 0
    balance = total_planned - total_actual

    # Daily trend
    daily_plans = plans.values('date').annotate(
        planned=Sum('quantity')
    ).order_by('date')
    actual_by_date = Production.objects.filter(planning_id__in=plan_ids).values('planning__date').annotate(
        actual=Sum('quantity')
    )
    actual_date_map = {str(item['planning__date']): item['actual'] for item in actual_by_date}

    kpis = {
        'total_planned': total_planned,
        'total_actual': total_actual,
        'completion_rate': completion_rate,
        'pending_plans': pending_plans,
        'balance': balance,
    }

    # Charts
    charts = {
        'planned_vs_actual': {
            'labels': [str(d['date']) for d in daily_plans],
            'planned': [float(d['planned'] or 0) for d in daily_plans],
            'actual': [float(actual_date_map.get(str(d['date']), 0)) for d in daily_plans],
        },
        'by_category': _get_grouped_data(plans, 'category', 'quantity'),
        'by_machine': _get_grouped_data(plans, 'machine__name', 'quantity'),
        'by_status': {
            'labels': ['Completed', 'In Progress', 'Pending'],
            'values': [
                sum(1 for p in plans if actual_map.get(p.id, 0) >= p.quantity),
                sum(1 for p in plans if 0 < actual_map.get(p.id, 0) < p.quantity),
                sum(1 for p in plans if actual_map.get(p.id, 0) == 0 and p.quantity > 0),
            ]
        }
    }

    # Table data
    table_data = []
    for p in plans.order_by('-date')[:200]:
        actual_qty = actual_map.get(p.id, 0)
        bal = p.quantity - actual_qty
        status = 'Completed' if bal <= 0 else ('In Progress' if actual_qty > 0 else 'Pending')
        completion = round((actual_qty / p.quantity * 100), 1) if p.quantity else 0

        table_data.append({
            'date': p.date.strftime('%d %b %Y'),
            'machine': p.machine.name if p.machine else '-',
            'category': p.category,
            'product': f"{p.thickness}mm" if p.thickness else '-',
            'size': f"{p.length}x{p.width}" if p.length and p.width else '-',
            'planned_qty': p.quantity,
            'actual_qty': actual_qty,
            'balance': bal,
            'completion_pct': completion,
            'status': status,
            'remark': p.remark or '-',
        })

    table_config = {
        'headers': ['#', 'Date', 'Machine', 'Category', 'Product', 'Size', 'Planned Qty',
                    'Actual Qty', 'Balance', 'Completion %', 'Status', 'Remark'],
        'keys': ['date', 'machine', 'category', 'product', 'size', 'planned_qty', 'actual_qty', 'balance', 'completion_pct', 'status', 'remark']
    }

    pivot_config = {
        'rows': ['Machine', 'Category', 'Status'],
        'cols': ['Status', 'Category'],
        'values': ['Planned Qty', 'Actual Qty', 'Balance'],
        'agg': ['sum', 'avg', 'count']
    }

    return {
        'kpis': kpis,
        'charts': charts,
        'table_data': table_data,
        'table_config': table_config,
        'pivot_data': table_data,
        'pivot_config': pivot_config,
    }


def _get_formulation_data(request, from_date, to_date, machine_ids, shift):
    """Generate detailed data for Formulation reports"""
    formulations = Formulation.objects.all().select_related('machine', 'planning', 'created_by')

    if hasattr(request, 'user') and hasattr(request.user, 'role') and request.user.role == 'Operator':
        formulations = formulations.filter(created_by=request.user)

    if from_date and to_date:
        try:
            formulations = formulations.filter(date__range=[from_date, to_date])
        except Exception:
            pass

    if machine_ids:
        formulations = formulations.filter(machine_id__in=machine_ids)
    if shift:
        formulations = formulations.filter(shift=shift)

    # Get formulation items
    form_ids = list(formulations.values_list('id', flat=True))
    items_qs = FormulationItem.objects.filter(formulation_id__in=form_ids).select_related('raw_material')

    # KPIs
    total_formulations = formulations.count()
    total_batches = formulations.aggregate(s=Sum('batches'))['s'] or 0
    approved = formulations.filter(status='Approved').count()
    pending = formulations.filter(status='Pending').count()
    loss_formulations = formulations.filter(is_loss=True).count()

    # Material summary
    material_summary = items_qs.values('raw_material__name').annotate(
        total_weight=Sum('weight')
    ).order_by('-total_weight')[:10]

    kpis = {
        'total_formulations': total_formulations,
        'total_batches': total_batches,
        'approved': approved,
        'pending': pending,
        'loss_count': loss_formulations,
    }

    # Charts
    charts = {
        'by_machine': _get_grouped_data(formulations, 'machine__name', 'id', Count('id')),
        'by_shift': _get_grouped_data(formulations, 'shift', 'id', Count('id')),
        'status': _get_grouped_data(formulations, 'status', 'id', Count('id')),
        'daily_trend': _get_daily_trend(formulations, 'date'),
        'by_material': {
            'labels': [m['raw_material__name'] for m in material_summary],
            'values': [float(m['total_weight'] or 0) for m in material_summary],
        }
    }

    # Table data with material details
    table_data = []
    for f in formulations.order_by('-date')[:200]:
        items = f.items.all()[:5]
        materials_str = ', '.join([item.raw_material.name for item in items]) if items else '-'
        table_data.append({
            'date': f.date.strftime('%d %b %Y'),
            'name': f.name,
            'machine': f.machine.name if f.machine else '-',
            'shift': f.shift,
            'batches': f.batches or 0,
            'status': f.status,
            'is_loss': 'Yes' if f.is_loss else 'No',
            'created_by': f.created_by.username if f.created_by else '-',
            'items': items.count(),
            'materials': materials_str,
            'planning_id': f.planning.id if f.planning else '-',
        })

    table_config = {
        'headers': ['#', 'Date', 'Name', 'Machine', 'Shift', 'Batches', 'Materials',
                     'Items', 'Status', 'Loss', 'Created By', 'Planning ID'],
        'keys': ['date', 'name', 'machine', 'shift', 'batches', 'materials', 'items', 'status', 'is_loss', 'created_by', 'planning_id']
    }

    pivot_config = {
        'rows': ['Machine', 'Shift', 'Status'],
        'cols': ['Status', 'Shift'],
        'values': ['Batches', 'Items'],
        'agg': ['sum', 'count']
    }

    return {
        'kpis': kpis,
        'charts': charts,
        'table_data': table_data,
        'table_config': table_config,
        'pivot_data': table_data,
        'pivot_config': pivot_config,
    }


def _get_stock_data(request, from_date, to_date):
    """Generate data for Product Stock (In/Out) reports"""
    stocks = Stock.objects.all().select_related('product', 'operator', 'delivery_challan')

    if from_date and to_date:
        try:
            stocks = stocks.filter(created_at__date__range=[from_date, to_date])
        except Exception:
            pass

    # KPIs
    total_in = stocks.filter(movement_type='IN').aggregate(s=Sum('quantity'))['s'] or 0
    total_out = stocks.filter(movement_type='OUT').aggregate(s=Sum('quantity'))['s'] or 0
    current_balance = total_in - total_out
    total_movements = stocks.count()

    kpis = {
        'total_in': total_in,
        'total_out': total_out,
        'current_balance': current_balance,
        'total_movements': total_movements,
    }

    # Chart: In/Out trend
    daily_data = stocks.values('created_at__date', 'movement_type').annotate(
        total_qty=Sum('quantity')
    ).order_by('created_at__date')

    in_by_date = defaultdict(float)
    out_by_date = defaultdict(float)
    for d in daily_data:
        date_str = str(d['created_at__date'])
        if d['movement_type'] == 'IN':
            in_by_date[date_str] = float(d['total_qty'] or 0)
        else:
            out_by_date[date_str] = float(d['total_qty'] or 0)

    all_dates = sorted(set(list(in_by_date.keys()) + list(out_by_date.keys())))

    charts = {
        'trend': {
            'labels': all_dates,
            'in': [in_by_date.get(d, 0) for d in all_dates],
            'out': [out_by_date.get(d, 0) for d in all_dates],
        },
        'by_product': _get_grouped_data_by_related(stocks, 'product__product_name', 'quantity'),
    }

    # Table data
    table_data = []
    for s in stocks.order_by('-created_at')[:200]:
        product_name = s.product.product_name if s.product else '-'
        table_data.append({
            'date': s.created_at.strftime('%d %b %Y'),
            'movement_type': s.movement_type,
            'product': product_name,
            'quantity': s.quantity,
            'operator': s.operator.username if s.operator else '-',
            'challan': s.delivery_challan.challan_no if s.delivery_challan else '-',
        })

    table_config = {
        'headers': ['#', 'Date', 'Type', 'Product', 'Qty', 'Operator', 'Challan'],
        'keys': ['date', 'movement_type', 'product', 'quantity', 'operator', 'challan']
    }

    pivot_config = {
        'rows': ['Product', 'Movement Type'],
        'cols': ['Movement Type'],
        'values': ['Quantity'],
        'agg': ['sum', 'count']
    }

    return {
        'kpis': kpis,
        'charts': charts,
        'table_data': table_data,
        'table_config': table_config,
        'pivot_data': table_data,
        'pivot_config': pivot_config,
    }


def _get_raw_material_data(request):
    """Generate data for Raw Material Stock reports"""
    materials = RawMaterial.objects.filter(is_active=True).prefetch_related(
        'rawmaterialstock_set'
    )

    # Get latest stock movements
    latest_stock = {}
    for rm in materials:
        latest = rm.rawmaterialstock_set.all()[:1]
        latest = latest[0] if latest else None
        if latest:
            latest_stock[rm.id] = {
                'quantity': float(latest.quantity),
                'rate': float(latest.rate_per_kg),
                'date': latest.created_at.strftime('%d %b %Y'),
            }
        else:
            latest_stock[rm.id] = {
                'quantity': float(rm.current_stock),
                'rate': 0,
                'date': '-',
            }

    # KPIs
    total_materials = materials.count()
    low_stock = sum(1 for m in materials if m.current_stock < m.one_day_requirement)
    total_stock_value = sum(
        float(m.current_stock) * float(latest_stock[m.id]['rate'] or 0)
        for m in materials
    )

    kpis = {
        'total_materials': total_materials,
        'low_stock': low_stock,
        'total_stock_value': round(total_stock_value, 2),
        'avg_stock': round(sum(m.current_stock for m in materials) / total_materials, 2) if total_materials else 0,
    }

    # Charts
    top_10 = materials.order_by('-current_stock')[:10]
    charts = {
        'stock_levels': {
            'labels': [m.name for m in top_10],
            'values': [float(m.current_stock) for m in top_10],
            'requirements': [float(m.one_day_requirement) for m in top_10],
        },
        'by_category': _get_grouped_data(materials, 'category', 'current_stock'),
    }

    # Table data
    table_data = []
    for m in materials:
        stock_info = latest_stock[m.id]
        table_data.append({
            'name': m.name,
            'category': m.category,
            'current_stock': float(m.current_stock),
            'one_day_req': float(m.one_day_requirement),
            'unit': 'kg',
            'last_updated': stock_info['date'],
            'rate': stock_info['rate'],
            'value': round(float(m.current_stock) * stock_info['rate'], 2),
            'status': 'Low Stock' if m.current_stock < m.one_day_requirement else 'OK',
        })

    table_config = {
        'headers': ['#', 'Material', 'Category', 'Current Stock', '1 Day Req', 'Unit', 'Rate', 'Value', 'Status'],
        'keys': ['name', 'category', 'current_stock', 'one_day_req', 'unit', 'last_updated', 'rate', 'value', 'status']
    }

    pivot_config = {
        'rows': ['Category', 'Status'],
        'cols': ['Status'],
        'values': ['Current Stock', 'Value'],
        'agg': ['sum', 'avg']
    }

    return {
        'kpis': kpis,
        'charts': charts,
        'table_data': table_data,
        'table_config': table_config,
        'pivot_data': table_data,
        'pivot_config': pivot_config,
    }


def _get_dispatch_data(request, from_date, to_date):
    """Generate data for Delivery Challan / Dispatch reports"""
    challans = DeliveryChallan.objects.all().prefetch_related('items__product')

    if from_date and to_date:
        try:
            challans = challans.filter(challan_date__range=[from_date, to_date])
        except Exception:
            pass

    # KPIs
    total_challans = challans.count()
    total_dispatched = 0
    total_amount = 0
    for c in challans:
        items_list = list(c.items.all())
        total_dispatched += float(sum(item.quantity for item in items_list))
        amt = 0
        for item in items_list:
            calc = _product_dispatch_amount_chart(item.product, item.quantity, c.rate)
            amt += float(calc['amount'] or 0)
        total_amount += amt
    unique_parties = challans.values('party_name').distinct().count()

    kpis = {
        'total_challans': total_challans,
        'total_dispatched': round(total_dispatched, 2),
        'total_amount': round(total_amount, 2),
        'unique_parties': unique_parties,
    }

    # Chart: Daily dispatch
    daily_data = challans.values('challan_date').annotate(
        count=Count('id'),
        total_items=Count('items')
    ).order_by('challan_date')
    charts = {
        'trend': {
            'labels': [str(d['challan_date']) for d in daily_data],
            'counts': [d['count'] for d in daily_data],
        },
        'by_party': _get_grouped_data(challans, 'party_name', 'id', Count('id')),
    }

    # Table data
    table_data = []
    for c in challans.order_by('-challan_date')[:200]:
        total_qty = sum(float(item.quantity) for item in c.items.all())
        total_amt = sum(
            float(_product_dispatch_amount_chart(item.product, item.quantity, c.rate)['amount'] or 0)
            for item in c.items.all()
        )
        table_data.append({
            'challan_no': c.challan_no,
            'date': c.challan_date.strftime('%d %b %Y'),
            'party': c.party_name,
            'vehicle_no': c.vehicle_no,
            'total_qty': round(total_qty, 2),
            'amount': round(total_amt, 2),
            'rate': float(c.rate),
            'gst_rate': float(c.gst_rate),
        })

    table_config = {
        'headers': ['#', 'Challan No', 'Date', 'Party', 'Vehicle', 'Qty', 'Amount', 'Rate', 'GST %'],
        'keys': ['challan_no', 'date', 'party', 'vehicle_no', 'total_qty', 'amount', 'rate', 'gst_rate']
    }

    pivot_config = {
        'rows': ['Party', 'Date'],
        'cols': ['Party'],
        'values': ['Amount', 'Qty'],
        'agg': ['sum', 'count']
    }

    return {
        'kpis': kpis,
        'charts': charts,
        'table_data': table_data,
        'table_config': table_config,
        'pivot_data': table_data,
        'pivot_config': pivot_config,
    }


def _product_dispatch_amount_chart(product, quantity, rate):
    """Simple dispatch amount calculation for charts"""
    from decimal import Decimal
    qty = Decimal(str(quantity or 0))
    rate_decimal = Decimal(str(rate or 0))

    if product.category == "Frame":
        if product.size and hasattr(product.size, 'rate') and product.size.rate and product.length:
            size_rate = Decimal(str(product.size.rate or 0))
            length = Decimal(str(product.length.length or 0))
            piece_rate = (size_rate * length).quantize(Decimal("0.01"))
            amount = (piece_rate * qty).quantize(Decimal("0.01"))
            return {'weight_per_qty': None, 'weight_per_sqft': None, 'rate_per_sqft': None,
                    'piece_rate': piece_rate, 'amount': amount}
        return {'weight_per_qty': Decimal("0.00"), 'weight_per_sqft': Decimal("0.00"),
                'rate_per_sqft': Decimal("0.00"), 'piece_rate': Decimal("0.00"), 'amount': Decimal("0.00")}

    if not (product.height and product.width and product.thickness and product.density):
        return {'weight_per_qty': Decimal("0.00"), 'weight_per_sqft': Decimal("0.00"),
                'rate_per_sqft': Decimal("0.00"), 'piece_rate': Decimal("0.00"), 'amount': Decimal("0.00")}

    height = Decimal(str(product.height.height or 0))
    width = Decimal(str(product.width.width or 0))
    thickness = Decimal(str(product.thickness.thickness or 0))
    density = Decimal(str(product.density.density or 0))

    height_m = height * Decimal("0.0254")
    width_m = width * Decimal("0.0254")
    thickness_m = thickness / Decimal("1000")
    weight_per_qty = (height_m * width_m * thickness_m * density).quantize(Decimal("0.01"))

    sqft_exact = (height * width) / Decimal("144")
    sqft_rounded = sqft_exact.quantize(Decimal("0.01"))
    if not sqft_rounded:
        return {'weight_per_qty': Decimal("0.00"), 'weight_per_sqft': Decimal("0.00"),
                'rate_per_sqft': Decimal("0.00"), 'piece_rate': Decimal("0.00"), 'amount': Decimal("0.00")}

    weight_per_sqft = (weight_per_qty / sqft_rounded).quantize(Decimal("0.01"))
    rate_per_sqft = (weight_per_sqft * rate_decimal).quantize(Decimal("0.01"))
    amount = (sqft_exact * rate_per_sqft * qty).quantize(Decimal("0.01"))
    piece_rate = (amount / qty).quantize(Decimal("0.01")) if qty else Decimal("0.00")

    return {'weight_per_qty': weight_per_qty, 'weight_per_sqft': weight_per_sqft,
            'rate_per_sqft': rate_per_sqft, 'piece_rate': piece_rate, 'amount': amount}


def _get_scrap_data(request, scraps, from_date, to_date, machine_ids):
    """Generate data for Scrap reports"""
    # scraps queryset is now passed in from caller (allows pre-filtering)

    if hasattr(request, 'user') and hasattr(request.user, 'role') and request.user.role == 'Operator':
        scraps = scraps.filter(production__operator=request.user)

    if from_date and to_date:
        try:
            scraps = scraps.filter(date__range=[from_date, to_date])
        except Exception:
            pass

    if machine_ids:
        scraps = scraps.filter(production__machine_id__in=machine_ids)

    # KPIs
    total_scrap_qty = scraps.aggregate(s=Sum('quantity'))['s'] or 0
    total_scrap_weight = scraps.aggregate(s=Sum('weight'))['s'] or 0
    side_patti = scraps.filter(production__sidepatti__gt=0).aggregate(s=Sum('quantity'))['s'] or 0
    line_setting = scraps.filter(production__linesetting__gt=0).aggregate(s=Sum('quantity'))['s'] or 0
    rejected = scraps.filter(production__rejected_quantity__gt=0).aggregate(s=Sum('quantity'))['s'] or 0

    kpis = {
        'total_scrap_qty': float(total_scrap_qty),
        'total_scrap_weight': round(float(total_scrap_weight), 2),
        'side_patti': float(side_patti),
        'line_setting': float(line_setting),
        'rejected': float(rejected),
    }

    # Charts
    charts = {
        'by_type': {
            'labels': ['Side Patti', 'Line Setting', 'Rejected'],
            'values': [float(side_patti), float(line_setting), float(rejected)],
        },
        'by_machine': _get_grouped_data_from_model(scraps, 'production__machine__name', 'quantity'),
        'by_shift': _get_grouped_data_from_model(scraps, 'production__shift', 'quantity'),
    }

    # Table data
    table_data = []
    for s in scraps.order_by('-date')[:200]:
        scrap_type = 'Unknown'
        if s.production.sidepatti > 0:
            scrap_type = 'Side Patti'
        elif s.production.linesetting > 0:
            scrap_type = 'Line Setting'
        elif s.production.rejected_quantity > 0:
            scrap_type = 'Rejected'

        table_data.append({
            'date': s.date.strftime('%d %b %Y'),
            'machine': s.production.machine.name if s.production and s.production.machine else '-',
            'operator': s.production.operator.full_name if s.production and s.production.operator else '-',
            'shift': s.production.shift if s.production else '-',
            'type': scrap_type,
            'qty': float(s.quantity),
            'weight': round(float(s.weight or 0), 2),
            'production_id': s.production.id if s.production else '-',
        })

    table_config = {
        'headers': ['#', 'Date', 'Machine', 'Operator', 'Shift', 'Type', 'Qty', 'Weight', 'Production ID'],
        'keys': ['date', 'machine', 'operator', 'shift', 'type', 'qty', 'weight', 'production_id']
    }

    pivot_config = {
        'rows': ['Machine', 'Shift', 'Type'],
        'cols': ['Shift'],
        'values': ['Qty', 'Weight'],
        'agg': ['sum', 'avg']
    }

    return {
        'kpis': kpis,
        'charts': charts,
        'table_data': table_data,
        'table_config': table_config,
        'pivot_data': table_data,
        'pivot_config': pivot_config,
    }


def _get_weight_sheet_data(request, from_date, to_date, machine_ids):
    """Generate data for Weight Sheet reports"""
    sheets = WeightSheet.objects.all().select_related('machine', 'operator')

    if from_date and to_date:
        try:
            sheets = sheets.filter(date__range=[from_date, to_date])
        except Exception:
            pass

    if machine_ids:
        sheets = sheets.filter(machine_id__in=machine_ids)

    # Calculate totals
    for sheet in sheets:
        sheet._totals = {
            'rows': sheet.total_rows,
            'weight': float(sheet.total_weight),
            'standard': float(sheet.total_standard_weight),
            'excess': float(sheet.total_excess),
            'excess_pct': float(sheet.total_excess_percent),
        }

    # KPIs
    total_sheets = sheets.count()
    total_weight = sum(s._totals['weight'] for s in sheets)
    total_standard = sum(s._totals['standard'] for s in sheets)
    total_excess = sum(s._totals['excess'] for s in sheets)
    avg_excess_pct = round(total_excess / total_standard * 100, 1) if total_standard else 0

    kpis = {
        'total_sheets': total_sheets,
        'total_weight': round(total_weight, 2),
        'standard_weight': round(total_standard, 2),
        'total_excess': round(total_excess, 2),
        'avg_excess_pct': avg_excess_pct,
    }

    # Charts
    charts = {
        'by_machine': _get_grouped_data(sheets, 'machine__name', 'total_weight', Sum('rows__weight_per_piece')),
        'by_shift': _get_grouped_data(sheets, 'shift', 'total_weight', Sum('rows__weight_per_piece')),
        'daily_trend': _get_daily_trend(sheets, 'date', Sum('rows__weight_per_piece')),
    }

    # Table data
    table_data = []
    for s in sheets.order_by('-date', '-created_at')[:200]:
        table_data.append({
            'date': s.date.strftime('%d %b %Y'),
            'machine': s.machine.name if s.machine else '-',
            'operator': s.operator.username if s.operator else '-',
            'shift': s.shift,
            'category': s.category,
            'rows': s.total_rows,
            'total_weight': round(s._totals['weight'], 2),
            'standard_weight': round(s._totals['standard'], 2),
            'excess': round(s._totals['excess'], 2),
            'excess_pct': round(s._totals['excess_pct'], 2),
        })

    table_config = {
        'headers': ['#', 'Date', 'Machine', 'Operator', 'Shift', 'Category', 'Rows',
                     'Total Weight', 'Standard Weight', 'Excess', 'Excess %'],
        'keys': ['date', 'machine', 'operator', 'shift', 'category', 'rows',
                 'total_weight', 'standard_weight', 'excess', 'excess_pct']
    }

    pivot_config = {
        'rows': ['Machine', 'Category', 'Shift'],
        'cols': ['Shift'],
        'values': ['Total Weight', 'Excess', 'Rows'],
        'agg': ['sum', 'avg']
    }

    return {
        'kpis': kpis,
        'charts': charts,
        'table_data': table_data,
        'table_config': table_config,
        'pivot_data': table_data,
        'pivot_config': pivot_config,
    }


def _get_unfinished_data(request, from_date, to_date):
    """Generate data for Unfinished Production reports"""
    unfinished = UnfinishedProduction.objects.all().select_related('product', 'production', 'production__machine')

    if from_date and to_date:
        try:
            unfinished = unfinished.filter(date__range=[from_date, to_date])
        except Exception:
            pass

    # KPIs
    total_qty = unfinished.aggregate(s=Sum('quantity'))['s'] or 0
    total_items = unfinished.count()
    unique_products = unfinished.values('product').distinct().count()
    today_unfinished = unfinished.filter(date=timezone.now().date()).count()

    kpis = {
        'total_qty': float(total_qty),
        'total_items': total_items,
        'unique_products': unique_products,
        'today_unfinished': today_unfinished,
    }

    # Charts
    charts = {
        'by_product': _get_grouped_data(unfinished, 'product__product_name', 'quantity'),
        'by_date': _get_daily_trend(unfinished, 'date', Sum('quantity')),
    }

    # Table data
    table_data = []
    for u in unfinished.order_by('-date')[:200]:
        table_data.append({
            'date': u.date.strftime('%d %b %Y'),
            'product': u.product.product_name if u.product else '-',
            'category': u.product.category if u.product else '-',
            'quantity': float(u.quantity),
            'production_id': u.production.id if u.production else '-',
            'machine': u.production.machine.name if u.production and u.production.machine else '-',
        })

    table_config = {
        'headers': ['#', 'Date', 'Product', 'Category', 'Qty', 'Machine', 'Production ID'],
        'keys': ['date', 'product', 'category', 'quantity', 'machine', 'production_id']
    }

    pivot_config = {
        'rows': ['Product', 'Category', 'Machine'],
        'cols': ['Category'],
        'values': ['Quantity'],
        'agg': ['sum', 'count']
    }

    return {
        'kpis': kpis,
        'charts': charts,
        'table_data': table_data,
        'table_config': table_config,
        'pivot_data': table_data,
        'pivot_config': pivot_config,
    }


# ==================== HELPER FUNCTIONS ====================

def _get_grouped_data(queryset, field, value_field, agg_func=Sum):
    """Group queryset by field and aggregate value_field"""
    data = queryset.values(field).annotate(
        total=agg_func if not callable(agg_func) else (agg_func(value_field) if value_field != 'id' else Count('id'))
    ).order_by('-total')[:10]

    labels = []
    values = []
    for d in data:
        key = field.split('__')[-1]
        labels.append(d[field] or '-')
        values.append(float(d['total'] or 0))

    return {'labels': labels, 'values': values}


def _get_grouped_data_by_related(queryset, field, value_field):
    """Group by related field"""
    return _get_grouped_data(queryset, field, value_field)


def _get_grouped_data_from_model(queryset, field, value_field):
    """Group data from model annotations"""
    data = queryset.values(field).annotate(
        total=Sum(value_field)
    ).order_by('-total')[:10]

    labels = []
    values = []
    for d in data:
        key = field.split('__')[-1]
        labels.append(d[field] or '-')
        values.append(float(d['total'] or 0))

    return {'labels': labels, 'values': values}


def _get_daily_trend(queryset, date_field, agg_func=Sum('id')):
    """Get daily trend data"""
    data = queryset.values(date_field).annotate(
        total=agg_func
    ).order_by(date_field)

    labels = [str(d[date_field]) for d in data]
    values = [float(d['total'] or 0) for d in data]

    return {'labels': labels, 'values': values}


# ==================== MAIN ORCHESTRATOR ====================

def get_report_data(request):
    """Main function to get data based on report type"""
    report_type = _get_report_type(request)

    from_date = request.GET.get("from_date", "")
    to_date = request.GET.get("to_date", "")
    machine_ids = request.GET.getlist("machine")
    shift = request.GET.get("shift", "")
    category = request.GET.get("category", "")
    operator_id = request.GET.get("operator", "")

    if report_type == "production":
        prods = Production.objects.all().select_related(
            'product', 'machine', 'operator', 'color', 'size', 'thickness',
            'density', 'length', 'width', 'height'
        )
        prods = _apply_operator_role_filter(prods, request.user)
        prods = _apply_date_filter(prods, from_date, to_date)
        prods = _apply_machine_filter(prods, machine_ids)
        if shift:
            prods = prods.filter(shift=shift)
        if category:
            prods = prods.filter(category=category)
        if operator_id:
            prods = prods.filter(operator_id=operator_id)
        return _get_production_data(request, prods, from_date, to_date)

    elif report_type == "planning":
        return _get_planning_data(request, from_date, to_date, machine_ids, category)

    elif report_type == "formulation":
        return _get_formulation_data(request, from_date, to_date, machine_ids, shift)

    elif report_type == "stock":
        return _get_stock_data(request, from_date, to_date)

    elif report_type == "raw_material":
        return _get_raw_material_data(request)

    elif report_type == "dispatch":
        return _get_dispatch_data(request, from_date, to_date)

    elif report_type == "scrap":
        scraps = ScrapLog.objects.all().select_related('production', 'production__machine', 'production__operator')
        scraps = _apply_operator_role_filter(scraps, request.user)
        scraps = _apply_date_filter(scraps, from_date, to_date)
        scraps = _apply_machine_filter_scraps(scraps, machine_ids)
        return _get_scrap_data(request, scraps, from_date, to_date, machine_ids)

    elif report_type == "weight_sheet":
        return _get_weight_sheet_data(request, from_date, to_date, machine_ids)

    elif report_type == "unfinished":
        return _get_unfinished_data(request, from_date, to_date)

    # Default to production
    prods = Production.objects.all().select_related(
        'product', 'machine', 'operator', 'color', 'size', 'thickness',
        'density', 'length', 'width', 'height'
    )
    prods = _apply_operator_role_filter(prods, request.user)
    prods = _apply_date_filter(prods, from_date, to_date)
    prods = _apply_machine_filter(prods, machine_ids)
    if shift:
        prods = prods.filter(shift=shift)
    if category:
        prods = prods.filter(category=category)
    if operator_id:
        prods = prods.filter(operator_id=operator_id)
    return _get_production_data(request, prods, from_date, to_date)
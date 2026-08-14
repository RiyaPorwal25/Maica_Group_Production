from django.contrib import admin
from .models import (
    CustomUser, Product, Machine, Production, Stock, MachineOperator,
    RolePermission, DensityName, Color, Thickness, Density, Size,
    Length, Width, Height, Planning, RawMaterial, Supplier,
    PurchaseInvoice, RawMaterialStock, Formulation, FormulationItem,
    WeightSheet, WeightSheetRow, UnfinishedProduction, ScrapLog,
    UserSession, BatchAddHistory, FormulationBatch
)
from django.contrib.auth.admin import UserAdmin

# ---- CustomUser ----
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'full_name', 'role', 'email', 'contact', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('full_name', 'contact', 'role', 'dob')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('full_name', 'contact', 'role', 'dob')}),
    )

# ---- Product ----
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'product_name', 'category')
    list_filter = ('category',)
    search_fields = ('product_name',)

# ---- Machine ----
class MachineAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

class DensityNameAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

# ---- Color ----
class ColorAdmin(admin.ModelAdmin):
    list_display = ('id', 'color', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('color',)

# ---- Thickness ----
class ThicknessAdmin(admin.ModelAdmin):
    list_display = ('id', 'thickness', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('thickness',)

# ---- Density ----
class DensityAdmin(admin.ModelAdmin):
    list_display = ('id', 'density', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('density',)

# ---- Size ----
class SizeAdmin(admin.ModelAdmin):
    list_display = ('id', 'size', 'standard_weight', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('size',)

# ---- Length ----
class LengthAdmin(admin.ModelAdmin):
    list_display = ('id', 'length', 'unit', 'original_value', 'is_active')
    list_filter = ('unit', 'is_active')
    search_fields = ('length', 'original_value')

# ---- Width ----
class WidthAdmin(admin.ModelAdmin):
    list_display = ('id', 'width', 'unit', 'original_value', 'is_active')
    list_filter = ('unit', 'is_active')
    search_fields = ('width', 'original_value')

# ---- Height ----
class HeightAdmin(admin.ModelAdmin):
    list_display = ('id', 'height', 'unit', 'original_value', 'is_active')
    list_filter = ('unit', 'is_active')
    search_fields = ('height', 'original_value')

# ---- Machine Operator ----
class MachineOperatorAdmin(admin.ModelAdmin):
    list_display = ('operator', 'category')
    list_filter = ('category',)
    search_fields = ('operator__username',)

# ---- Production ----
class ProductionAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'machine', 'quantity', 'shift', 'operator', 'created_at')
    list_filter = ('shift', 'machine', 'operator')
    search_fields = ('product__product_name', 'machine__name', 'operator__username')
    exclude = ('planning',)  # Hide internal connection field

# ---- Stock ----
class StockAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'quantity', 'movement_type', 'operator', 'created_at')
    list_filter = ('movement_type', 'product', 'operator')
    search_fields = ('product__product_name', 'operator__username')

# ---- Planning ----
class PlanningAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'quantity', 'weight', 'remark', 'created_at')
    list_filter = ('category', 'remark', 'created_at')
    search_fields = ('category', 'remark')
    readonly_fields = ('created_at', 'updated_at')

# ---- Raw Material ----
class RawMaterialAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'current_stock', 'one_day_requirement', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'category')

# ---- Supplier ----
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'contact_person', 'phone')
    search_fields = ('name', 'contact_person', 'phone')

# ---- Purchase Invoice ----
class PurchaseInvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'supplier', 'invoice_no', 'invoice_date', 'receiving_date')
    list_filter = ('supplier', 'invoice_date', 'receiving_date')
    search_fields = ('invoice_no', 'supplier__name')

# ---- Raw Material Stock ----
class RawMaterialStockAdmin(admin.ModelAdmin):
    list_display = ('id', 'raw_material', 'quantity', 'movement_type', 'batch_history', 'formulation', 'created_at')
    list_filter = ('movement_type', 'raw_material', 'created_at')
    search_fields = ('raw_material__name', 'batch_history__group_name', 'formulation__name')

# ---- Formulation ----
class FormulationAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'machine', 'shift', 'status', 'created_by', 'date', 'is_loss')
    list_filter = ('shift', 'status', 'machine', 'is_loss', 'date')
    search_fields = ('name', 'machine__name', 'created_by__username')
    readonly_fields = ('date', 'created_by')
    exclude = ('production',)  # Hide internal connection field

# ---- Formulation Item ----
class FormulationItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'formulation', 'raw_material', 'weight')
    list_filter = ('formulation', 'raw_material')
    search_fields = ('formulation__name', 'raw_material__name')

# ---- Weight Sheet ----
class WeightSheetAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'machine', 'operator', 'shift', 'category', 'total_weight', 'total_excess_percent')
    list_filter = ('shift', 'category', 'machine', 'date')
    search_fields = ('machine__name', 'operator__username')
    readonly_fields = ('total_rows', 'total_weight', 'total_standard_weight', 'total_excess', 'total_excess_percent')

# ---- Weight Sheet Row ----
class WeightSheetRowAdmin(admin.ModelAdmin):
    list_display = ('id', 'sheet', 'color', 'weight_per_piece', 'standard_weight', 'excess')
    list_filter = ('sheet__category', 'color')
    search_fields = ('sheet__date', 'color__color')

# ---- Unfinished Production ----
class UnfinishedProductionAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'production', 'quantity', 'date')
    list_filter = ('date', 'product')
    search_fields = ('product__product_name',)

# ---- Scrap Log ----
class ScrapLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'production', 'quantity', 'weight', 'date')
    list_filter = ('date',)
    search_fields = ('production__id',)

# ---- BatchAddHistory ----
class FormulationBatchInline(admin.TabularInline):
    model = FormulationBatch
    extra = 0
    fields = ('raw_material', 'weight', 'date', 'shift')
    readonly_fields = ('raw_material', 'weight', 'date', 'shift')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False

class BatchAddHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'group_name', 'batch_count', 'date', 'shift', 'machine', 'added_by', 'created_at')
    list_filter = ('shift', 'date', 'machine')
    search_fields = ('group_name', 'added_by__username', 'added_by__full_name')
    readonly_fields = ('formulation', 'group_name', 'batch_count', 'date', 'shift', 'machine', 'added_by', 'created_at')
    inlines = [FormulationBatchInline]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

# ---- FormulationBatch ----
class FormulationBatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'batch_history', 'raw_material', 'weight', 'date', 'shift')
    list_filter = ('shift', 'date')
    search_fields = ('raw_material__name', 'batch_history__group_name')

# ---- User Session ----
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'date', 'login_time', 'logout_time')
    list_filter = ('date', 'user')
    search_fields = ('user__username', 'user__full_name')
    readonly_fields = ('date',)

# ---- Role Permission ----
class RolePermissionAdmin(admin.ModelAdmin):
    list_display = ('role', 'module', 'has_permission')
    list_filter = ('role', 'module', 'has_permission')
    search_fields = ('role', 'module')
    fieldsets = (
        ('Permission Details', {
            'fields': ('role', 'module', 'has_permission')
        }),
    )

# ---- Register ----
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Machine, MachineAdmin)
admin.site.register(MachineOperator, MachineOperatorAdmin)
admin.site.register(Production, ProductionAdmin)
admin.site.register(Stock, StockAdmin)
admin.site.register(RolePermission, RolePermissionAdmin)
admin.site.register(DensityName, DensityNameAdmin)
admin.site.register(Color, ColorAdmin)
admin.site.register(Thickness, ThicknessAdmin)
admin.site.register(Density, DensityAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(Length, LengthAdmin)
admin.site.register(Width, WidthAdmin)
admin.site.register(Height, HeightAdmin)
admin.site.register(Planning, PlanningAdmin)
admin.site.register(RawMaterial, RawMaterialAdmin)
admin.site.register(Supplier, SupplierAdmin)
admin.site.register(PurchaseInvoice, PurchaseInvoiceAdmin)
admin.site.register(RawMaterialStock, RawMaterialStockAdmin)
admin.site.register(Formulation, FormulationAdmin)
admin.site.register(FormulationItem, FormulationItemAdmin)
admin.site.register(WeightSheet, WeightSheetAdmin)
admin.site.register(WeightSheetRow, WeightSheetRowAdmin)
admin.site.register(UnfinishedProduction, UnfinishedProductionAdmin)
admin.site.register(ScrapLog, ScrapLogAdmin)
admin.site.register(BatchAddHistory, BatchAddHistoryAdmin)
admin.site.register(FormulationBatch, FormulationBatchAdmin)
admin.site.register(UserSession, UserSessionAdmin)

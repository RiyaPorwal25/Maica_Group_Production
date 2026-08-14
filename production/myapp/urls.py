from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    #home page
    path('dashboard/', views.dashboard, name='dashboard'),

    #dashboard 
    path("dashboard_v2/", views.dashboard_v2, name="dashboard_v2"),
    path("mobile/dashboard/", views.mobile_dashboard, name="mobile_dashboard"),
    

    path('stock/',views.stock_view,name='stock'),
    path('mobile/stock/', views.mobile_stock, name='mobile_stock'),
    # path("planning/", views.planning_view, name="planning"),
    path("product/<int:pk>/history-json/", views.product_stock_history_json, name="product_history_json"),
    path('product/', views.product_list, name='product_list'),

    path("unfinished/", views.unfinished_list, name="unfinished_list"),
    path("unfinished/<int:item_id>/convert/", views.convert_unfinished, name="convert_unfinished"),
    path("unfinished/<int:item_id>/add-to-scrap/", views.add_to_scrap, name="add_to_scrap"),
    
    path("user/", views.user_list, name="user_list"),

    path("export-stock/", views.export_stock_csv, name="export_stock"),
    path('product/delete/<int:product_id>/', views.delete_product, name='delete_product'),
    path('production/',views.production_view, name='production'),
    path('production/approve/<int:production_id>/', views.approve_production, name='approve_production'),
    path('edit-production/<int:production_id>/', views.edit_production, name='edit_production'),


    path("weightsheets/", views.weight_sheet, name="weight_sheet"),
    path("weightsheets/<int:pk>/", views.weight_sheet, name="weight_sheet_detail"),
    # path("production/<int:production_id>/weight-sheet/", views.weight_sheet, name="weight_sheet"),

    path('api/operators-by-machine/', views.get_operators_for_machine, name='get_operators_for_machine'),  # New API

    # WeightSheet JSON API
    path('api/weightsheets/', views.weight_sheet_api, name='api_weight_sheets'),
    path('api/weightsheets/<int:pk>/', views.weight_sheet_detail_api, name='api_weight_sheet_detail'),

    path('machine/', views.machine_list, name='machine_list'),
    path('machine/delete/<int:pk>/', views.delete_machine, name='delete_machine'),
    path('machine-operator/', views.machine_operator_list, name='machine_operator_list'),


    path("master/color/", views.color_list, name="color_list"),
    path("master/density/", views.density_list, name="density_list"),
    path("master/thickness/", views.thickness_list, name="thickness_list"),
    path("master/size/", views.size_list, name="size_list"),
    path("master/length/", views.length_list, name="length_list"),
    path("master/height/", views.height_list, name="height_list"),
    path("master/width/", views.width_list, name="width_list"),
    path('master/density-name/', views.density_name_list, name='density_name_list'),
    path("master/party/", views.party_list, name="party_list"),

    path("delete/color/<int:pk>/", views.delete_color, name="delete_color"),
    path("delete/density/<int:pk>/", views.delete_density, name="delete_density"),
    path("delete/thickness/<int:pk>/", views.delete_thickness, name="delete_thickness"),
    path("delete/size/<int:pk>/", views.delete_size, name="delete_size"),
    path("delete/length/<int:pk>/", views.delete_length, name="delete_length"),
    path("delete/height/<int:pk>/", views.delete_height, name="delete_height"),
    path("delete/width/<int:pk>/", views.delete_width, name="delete_width"),
    path('delete-density-name/<int:pk>/', views.delete_density_name, name='delete_density_name'),
    path("delete/party/<int:pk>/", views.delete_party, name="delete_party"),


    path("reports/", views.reports, name="reports"),
    path('export-report/', views.export_report, name='export_report'),

    path('calculator/', views.density_rate_calculator, name='calculator'),

    # API endpoints for creating new dropdown values
    path('api/create-size/', views.api_create_size, name='api_create_size'),
    path('api/create-color/', views.api_create_color, name='api_create_color'),
    path('api/create-length/', views.api_create_length, name='api_create_length'),
    path('api/create-thickness/', views.api_create_thickness, name='api_create_thickness'),
    path('api/create-height/', views.api_create_height, name='api_create_height'),
    path('api/create-width/', views.api_create_width, name='api_create_width'),
    path('api/create-density/', views.api_create_density, name='api_create_density'),

    path('export-dashboard-report/', views.export_dashboard_report, name='export_dashboard_report'),

    # upload production url from excel
    path('upload-excel/', views.upload_excel, name='upload_excel'),

    # consumption urls
    path("formulation/", views.formulation_page, name="formulation_page"),
    path("formulation/frameline/", views.frameline_page, name="frameline_page"),
    # path("formulation/doorline/", views.doorline_page, name="doorline_page"),
    path("formulation/batch-issue/", views.batch_issue_page, name="batch_issue_page"),
    path("delete-formulation/<int:id>/", views.delete_formulation, name="delete_formulation"),
    path("formulation/add-batch/<int:id>/", views.add_batch, name="add_batch"),
    path("formulation/approve/<int:id>/", views.approve_formulation, name="approve_formulation"),
    path("formulation/edit-loss-formula/",views.edit_loss_formula,name="edit_loss_formula"),
    path("formulation/edit/<int:id>/", views.edit_formulation, name="edit_formulation"),

    path("formulation/upload/", views.upload_formulation, name="upload_formulation"),
    

    path('raw-materials/', views.raw_material_list, name='raw_material_list'),
    path('raw-material/history/<int:rm_id>/', views.raw_material_history, name='raw_material_history'),
    path('raw-material/history/download/<int:rm_id>/', views.raw_material_history_download, name='raw_material_history_download'),
    path('add-stock/', views.add_stock, name='add_stock'),
    path('raw-material/costing-details/', views.costing_details, name='costing_details'),
    path('mobile/raw-materials/', views.mobile_raw_materials, name='mobile_raw_materials'),
    path('mobile/dispatch/', views.mobile_dispatch, name='mobile_dispatch'),

    path('roles_responsibilities/',views.roles_responsibilities,name="roles_responsibilities"),
    path('planning/', views.planning_door_sheet, name='planning_door_sheet'),
    path('planning/frame-sheet/', views.planning_frame_sheet, name='planning_frame_sheet'),
    path('planning/detail/<int:pk>/', views.planning_detail_json, name='planning_detail_json'),
    path('planning/delete/<int:pk>/', views.delete_planning, name='delete_planning'),
    path('scrap/', views.scrap_list, name='scrap_list'),
    path('scrap/export/', views.export_scrap_report, name='export_scrap_report'),

    # Production 2.0 URLs
    path('production-2-0/door/', views.production_2_0_door, name='production_2_0_door'),
    path('production-2-0/frame/', views.production_2_0_frame, name='production_2_0_frame'),
    path('production-2-0/frame/template/', views.download_production_template, {'category': 'Frame'}, name='production_2_0_frame_template'),
    path('production-2-0/door/template/', views.download_production_template, {'category': 'Door'}, name='production_2_0_door_template'),
    path('production-2-0/frame/upload/', views.upload_production_excel, {'category': 'Frame'}, name='production_2_0_frame_upload'),
    path('production-2-0/door/upload/', views.upload_production_excel, {'category': 'Door'}, name='production_2_0_door_upload'),
    path('api/reorder-groups/', views.reorder_groups, name='reorder_groups'),
    
    path('dispatch/', views.dispatch, name='dispatch'),
    path('dispatch/<int:pk>/edit/', views.dispatch_edit, name='dispatch_edit'),
    path('dispatch/<int:pk>/edit-qty/', views.dispatch_edit_qty, name='dispatch_edit_qty'),
    path('dispatch/challan/<int:pk>/pdf/', views.delivery_challan_pdf, name='delivery_challan_pdf'),
    path('api/get-last-formulation/<str:group_key>/', views.get_last_formulation, name='get_last_formulation'),
    path('api/get-formulation-by-group/', views.get_formulation_by_group, name='get_formulation_by_group'),
    path('api/group-batch-input/', views.api_group_batch_input, name='api_group_batch_input'),
    path('api/group-approve/', views.api_group_approve, name='api_group_approve'),
    path('api/group-edit/', views.api_group_edit, name='api_group_edit'),
    path('api/group-add-stock-deduct/', views.api_group_add_stock_deduct, name='api_group_add_stock_deduct'),

    # Power BI Dashboard URLs
    path('power-bi/', views.power_bi_report, name='power_bi_report'),
    path('power-bi/data/', views.power_bi_data, name='power_bi_data'),
    path('power-bi/save/', views.save_dashboard, name='save_dashboard'),
    path('power-bi/list/', views.list_dashboards, name='list_dashboards'),
    path('power-bi/load/<int:dashboard_id>/', views.load_dashboard, name='load_dashboard'),
    path('power-bi/delete/<int:dashboard_id>/', views.delete_dashboard, name='delete_dashboard'),

    # User Sessions URLs (Admin/Manager only)
    path('user-sessions/', views.user_sessions, name='user_sessions'),

    # Logs URLs (Admin only)
    path('logs/', views.logs_view, name='logs'),
    path('api/logs/', views.logs_api, name='logs_api'),
]


# okay
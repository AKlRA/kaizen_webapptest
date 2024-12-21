from django.contrib import admin
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('fetch-kaizen-sheet/<int:kaizen_id>/', views.fetch_kaizen_sheet, name='fetch_kaizen_sheet'),
    path('employee-dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('download-kaizen-sheet/<int:kaizen_id>/', views.download_kaizen_sheet, name='download_kaizen_sheet'),
    path('create-temp-kaizen/', views.create_temp_kaizen, name='create_temp_kaizen'),
    path('upload-handwritten-sheet/', views.upload_handwritten_sheet, name='upload_handwritten_sheet'),
    path('coordinator-dashboard/', views.coordinator_dashboard, name='coordinator_dashboard'),
    path('get-yearly-data/<int:year>/', views.get_yearly_data, name='get_yearly_data'),
    path('cip-register/', views.cip_register_view, name='cip_register'),
    path('update-kaizen/<int:kaizen_id>/', views.update_kaizen, name='update_kaizen'),
    path('hod-dashboard/', views.hod_dashboard, name='hod_dashboard'),
    path('view-kaizen/<int:kaizen_id>/', views.view_kaizen, name='view_kaizen'),
    path('view-sheet/<int:sheet_id>/', views.view_sheet, name='view_sheet'),    
    path('approve-kaizen/<int:kaizen_id>/', views.approve_kaizen, name='approve_kaizen'),
    path('coordinator-approve-kaizen/<int:kaizen_id>/', views.coordinator_approve_kaizen, name='coordinator_approve_kaizen'),
    path('get-employee-submissions/<int:employee_id>/', views.get_employee_submissions, name='get_employee_submissions'),
    path('finance-dashboard/', views.finance_dashboard, name='finance_dashboard'),
    path('finance-approve-kaizen/<int:kaizen_id>/', views.finance_approve_kaizen, name='finance_approve_kaizen'),
    path('get-cost-details/<int:kaizen_id>/', views.get_cost_details, name='get_cost_details'),
    path('save-kaizen-coordinators/', views.save_kaizen_coordinators, name='save_kaizen_coordinators'),
    path('get-excel-template/<str:template_name>/', views.get_excel_template, name='get_excel_template'),
    path('get-department-data/<int:year>/<int:month>/', views.get_department_data, name='get_department_data'),
    
    
    ] 
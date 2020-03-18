from django.urls import path, include

from .views import FileUploadView, CsvToDatabase, VendorsCreateView, AdministratorDashboard, VendorsToFrontView, \
    ModulesListView


urlpatterns = [
    path('csv_upload/', FileUploadView.as_view(), name='csv_upload'),
    path('from_csv_create/', CsvToDatabase.as_view(), name='csv_vendor_create'),
    path('create/', VendorsCreateView.as_view(), name='vendor_create'),
    path('administrator_dashboard/', AdministratorDashboard.as_view(), name='administartor_dashboard'),
    path('vendors_list/', VendorsToFrontView.as_view(), name='vendors_list'),
    path('modules_list/', ModulesListView.as_view())

]
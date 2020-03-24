from django.urls import path, include

from .views import FileUploadView, CsvToDatabase, VendorsCreateView, AdministratorDashboard, VendorsToFrontView, \
    ModulesListView, VendorManagementList, VendorProfileUpdateView, VendorContactsCreateView, ContactsUpdateView


urlpatterns = [
    path('csv_upload/', FileUploadView.as_view(), name='csv_upload'),
    path('from_csv_create/', CsvToDatabase.as_view(), name='csv_vendor_create'),
    path('create/', VendorsCreateView.as_view(), name='vendor_create'),
    path('administrator_dashboard/', AdministratorDashboard.as_view(), name='administartor_dashboard'),
    path('vendors_list/', VendorsToFrontView.as_view(), name='vendors_list'),
    path('modules_list/', ModulesListView.as_view()),
    path('vendor_management_list/', VendorManagementList.as_view()),
    path('<int:vendorid>/', VendorProfileUpdateView.as_view(), name='vendor_update'),
    # path('<int:vendorid>/contact_create/', VendorContactsCreateView.as_view(), name='contact_create'),
    path('contact_create/', VendorContactsCreateView.as_view(), name='contact_create'),
    path('contact/<int:contact_id>/update/', ContactsUpdateView.as_view(), name='contact_update'),
]
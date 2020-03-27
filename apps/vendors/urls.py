from django.urls import path, include

from .views import FileUploadView, CsvToDatabase, VendorsCreateView, AdministratorDashboard, VendorsToFrontView, \
    ModulesListView, VendorManagementList, VendorProfileUpdateView, VendorContactsCreateView, ContactsUpdateView, \
    NewRfiRoundCreateView, RfiRoundClose, RfiRoundUpdateView, AssosiateModulesWithVendorView, VendorProfileModulesList, \
    VendorProfileModulesListUpdate


urlpatterns = [
    path('csv_upload/', FileUploadView.as_view(), name='csv_upload'),
    path('from_csv_create/', CsvToDatabase.as_view(), name='csv_vendor_create'),
    path('create/', VendorsCreateView.as_view(), name='vendor_create'),
    path('administrator_dashboard/', AdministratorDashboard.as_view(), name='administartor_dashboard'),
    path('vendors_list/', VendorsToFrontView.as_view(), name='vendors_list'),
    path('modules_list/', ModulesListView.as_view()),
    path('vendor_management_list/', VendorManagementList.as_view()),
    # vendor profile
    path('<int:vendorid>/', VendorProfileUpdateView.as_view(), name='vendor_update'),
    path('contact_create/', VendorContactsCreateView.as_view(), name='contact_create'),
    path('contact/<int:contact_id>/update/', ContactsUpdateView.as_view(), name='contact_update'),
    path('<int:vendorid>/modules/', VendorProfileModulesList.as_view(), name='modules_get'),
    path('<int:pk>/modules_update/', VendorProfileModulesListUpdate.as_view(), name='modules_update'),
    # rfi
    path('rfi_create/', NewRfiRoundCreateView.as_view(), name='rfi_create'),
    path('rfi/<str:rfiid>/close/', RfiRoundClose.as_view(), name='rfi_close'),
    path('rfi/<str:rfiid>/update/', RfiRoundUpdateView.as_view(), name='rfi_update'),
    path('module_to_vendor_list/', AssosiateModulesWithVendorView.as_view(), name='assign_module_to_vendor'),
]
from django.urls import path, include

from .views import FileUploadView, RfiCsvUploadView, CsvToDatabase, VendorsCreateView, AdministratorDashboard, VendorsToFrontView, \
    ModulesListView, VendorManagementListScreen, VendorProfileUpdateView, VendorContactsCreateView, ContactsUpdateView, \
    NewRfiRoundCreateView, RfiRoundClose, RfiRoundView, AssociateModulesWithVendorView, \
    VendorProfileModulesListCreate, RfiRoundListView, VendorProfilePageView, AssociateModulesWithVendorCsv,\
    CsvRfiTemplateDownload, ExcelFileUploadView, UploadElementFromExcelFile, AnalystListView, VendorsActiveToFrontView, \
    DownloadRfiExcelFile, InfoToDownloadRfiExcelFile, ElementInitializeFromExcelFile, VendorActivityReportView, \
    DashboardVendors


urlpatterns = [
    # file parsing
    path('excel_upload/<str:rfiid>/<int:vendor>/', ExcelFileUploadView.as_view(), name='excel_rfi_upload'),
    # path('excel_upload/<str:ci>/', ExcelFileUploadView.as_view(), name='excel_ci_upload'),
    path('csv_upload/', FileUploadView.as_view(), name='csv_upload'),
    #
    path('from_csv_create/', CsvToDatabase.as_view(), name='csv_vendor_create'),
    path('create/', VendorsCreateView.as_view(), name='vendor_create'),
    path('administrator_dashboard/', AdministratorDashboard.as_view(), name='administartor_dashboard'),
    path('vendors_list/', VendorsToFrontView.as_view(), name='vendors_list'),
    path('active_vendors_list/', VendorsActiveToFrontView.as_view(), name='active_vendors_list'),
    path('analyst_list/', AnalystListView.as_view(), name='analyst_list'),
    path('modules_list/', ModulesListView.as_view()),
    path('vendor_management_screen/', VendorManagementListScreen.as_view(), name='vendor_management_screen'),
    # vendor profile
    # path('<int:vendorid>/profile/', VendorProfilePageView.as_view(), name='vendor_profile'),
    path('<int:vendorid>/', VendorProfileUpdateView.as_view(), name='vendor_update'),
    path('contact_create/', VendorContactsCreateView.as_view(), name='contact_create'),
    path('contact/<int:contact_id>/update/', ContactsUpdateView.as_view(), name='contact_update'),
    path('<int:vendorid>/modules/', VendorProfileModulesListCreate.as_view(), name='modules_to_vendor'),
    # rfi
    path('rfi_create/', NewRfiRoundCreateView.as_view(), name='rfi_create'),
    path('rfi/list/', RfiRoundListView.as_view(), name='rfi_list'),
    path('rfi/<str:rfiid>/close/', RfiRoundClose.as_view(), name='rfi_close'),
    path('rfi/<str:rfiid>/', RfiRoundView.as_view(), name='rfi_management'),
    path('rfi/<str:rfiid>/vendor_module_to_round_list/', AssociateModulesWithVendorView.as_view(),
         name='vendor_module_to_round'),
    path('rfi_csv_upload/', RfiCsvUploadView.as_view(), name='rfi_csv_upload'),
    path('rfi_csv_update/', AssociateModulesWithVendorCsv.as_view(), name='rfi_csv_update'),
    path('<str:rfiid>/rfi_csv_template_download/', CsvRfiTemplateDownload.as_view(), name='rfi_csv_download'),
    # from excell to db upload
    path('upload_excel_rfi/<str:rfiid>/<int:vendor>/<int:analyst>/', UploadElementFromExcelFile.as_view(),
                                                                        name='from_excel_element_upload'),
    path('get_info_for_download_excel/<str:rfiid>/', InfoToDownloadRfiExcelFile.as_view(), name='before_download_excel'),
    path('download_rfi_archive/', DownloadRfiExcelFile.as_view(), name='download_excel'),
    path('initialize_default_rfi_element/', ElementInitializeFromExcelFile.as_view(), name='default_rfi_element'),
    # Vendor activity report
    path('activity_report/<int:vendorid>/', VendorActivityReportView.as_view(), name='vendor_activity_report'),
    path('dashboard/vendors/', DashboardVendors.as_view(), name='dashboard_vendors'),
]

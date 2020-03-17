from django.urls import path, include

from .views import FileUploadView, CsvToDatabase, VendorsCreateView, AdministratorDashboard, VendorsToFrontView


urlpatterns = [
    path('csv_upload/', FileUploadView.as_view()),
    # path('from_csv_create/', CsvToDatabase.as_view()),
    path('create/', VendorsCreateView.as_view(), name='vendor_create'),
    path('administrator_dashboard/', AdministratorDashboard.as_view(), name='administartor_dashboard'),
    path('vendors_list/', VendorsToFrontView.as_view(), name='vendors_list'),

]
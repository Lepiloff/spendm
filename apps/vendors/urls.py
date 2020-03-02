from django.contrib import admin
from django.urls import path, include

from .views import FileUploadView, CsvToDatabase, VendorsCreateView, AdministratorDashboard


urlpatterns = [
    path('csv_upload/', FileUploadView.as_view()),
    path('from_csv_create/', CsvToDatabase.as_view()),
    path('create/', VendorsCreateView.as_view()),
    path('administrator_dashboard/', AdministratorDashboard.as_view(), name='administartor_dashboard'),

]
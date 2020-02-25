from django.contrib import admin
from django.urls import path, include

from .views import FileUploadView, CsvToDatabase


urlpatterns = [
    path('csv_upload/', FileUploadView.as_view()),
    path('from_csv_create/', CsvToDatabase.as_view()),

]
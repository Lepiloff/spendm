from django.contrib import admin
from .models import Modules, VendorModuleNames, VendorContacts, Vendors

admin.site.register(Modules)
admin.site.register(VendorModuleNames)
admin.site.register(VendorContacts)
admin.site.register(Vendors)
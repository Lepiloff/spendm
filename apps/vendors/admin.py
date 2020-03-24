from django.contrib import admin
from .models import Modules, VendorModuleNames, VendorContacts, Vendors, Rfis, RfiParticipation, RfiParticipationStatus

admin.site.register(Modules)
admin.site.register(VendorModuleNames)
admin.site.register(VendorContacts)
admin.site.register(Vendors)
admin.site.register(Rfis)
admin.site.register(RfiParticipation)
admin.site.register(RfiParticipationStatus)
from django.contrib import admin
from .models import Modules, VendorModuleNames, VendorContacts, Vendors, Rfis, RfiParticipation, RfiParticipationStatus, \
    ParentCategories, Elements, Subcategories, Categories, AnalystNotes, SmScores, Attachments, AssignedVendorsAnalysts

admin.site.register(Modules)
admin.site.register(VendorModuleNames)
admin.site.register(VendorContacts)
admin.site.register(Vendors)
admin.site.register(Rfis)
admin.site.register(RfiParticipation)
admin.site.register(RfiParticipationStatus)
admin.site.register(ParentCategories)
admin.site.register(Elements)
admin.site.register(Subcategories)
admin.site.register(Categories)
admin.site.register(AnalystNotes)
admin.site.register(SmScores)
admin.site.register(Attachments)
admin.site.register(AssignedVendorsAnalysts)

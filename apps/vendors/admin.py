from django.contrib import admin
from .models import Modules, VendorModuleNames, VendorContacts, Vendors, Rfis, RfiParticipation, RfiParticipationStatus, \
    ParentCategories, Elements, Subcategories, Categories, AnalystNotes, SmScores, Attachments, AssignedVendorsAnalysts, \
    CompanyGeneralInfoQuestion, CompanyGeneralInfoAnswers, ElementsAttachments, SelfScores, SelfDescriptions, \
    ModulesParentCategories, ModulesParentCategories


class ElementsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'element_name', 'initialize',)
    list_display_links = ['pk', ]
    list_filter = ['initialize', ]
    search_fields = ('element_name', 's__subcategory_name',)


class VendorsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'vendor_name',)
    list_display_links = ['pk', ]
    list_filter = ['active', ]


class SubcategoriesAdmin(admin.ModelAdmin):
    list_display = ('sid', 'subcategory_name',)
    list_display_links = ['sid', ]
    search_fields = ('c__category_name',)


class ModulesParentCategories(admin.TabularInline):
    model = ModulesParentCategories
    extra = 1


class ModulesAdmin(admin.ModelAdmin):
    model = Modules
    inlines = (ModulesParentCategories, )


class ParentCategoriesAdmin(admin.ModelAdmin):
    model = ParentCategories
    inlines = (ModulesParentCategories, )


admin.site.register(Modules, ModulesAdmin)
admin.site.register(ParentCategories, ParentCategoriesAdmin)
admin.site.register(VendorModuleNames)
admin.site.register(VendorContacts)
admin.site.register(Vendors, VendorsAdmin)
admin.site.register(Rfis)
admin.site.register(RfiParticipation)
admin.site.register(RfiParticipationStatus)
admin.site.register(Elements, ElementsAdmin)
admin.site.register(Subcategories, SubcategoriesAdmin)
admin.site.register(Categories)
admin.site.register(AnalystNotes)
admin.site.register(SmScores)
admin.site.register(Attachments)
admin.site.register(ElementsAttachments)
admin.site.register(AssignedVendorsAnalysts)
admin.site.register(CompanyGeneralInfoQuestion)
admin.site.register(CompanyGeneralInfoAnswers)
admin.site.register(SelfScores)
admin.site.register(SelfDescriptions)



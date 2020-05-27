from django.db import migrations


def forwards_func(apps, schema_editor):
    ModulesParentCategories = apps.get_model('vendors', 'ModulesParentCategories')
    Modules = apps.get_model('vendors', 'Modules')
    ParentCategories = apps.get_model('vendors', 'ParentCategories')

    common_s2p_category, _ = ParentCategories.objects.get_or_create(parent_category_name='COMMON S2P')
    common_sourcing_sxm_category, _ = ParentCategories.objects.get_or_create(
        parent_category_name='COMMON SOURCING – SXM')
    services_category, _ = ParentCategories.objects.get_or_create(parent_category_name='SERVICES')
    sourcing_category, _ = ParentCategories.objects.get_or_create(parent_category_name='SOURCING')
    sxm_category, _ = ParentCategories.objects.get_or_create(parent_category_name='SXM')
    spend_analytics_category, _ = ParentCategories.objects.get_or_create(parent_category_name='Spend Analytics')
    clm_category, _ = ParentCategories.objects.get_or_create(parent_category_name='CLM')
    e_procurement_category, _ = ParentCategories.objects.get_or_create(parent_category_name='eProcurement')
    i2p_category, _ = ParentCategories.objects.get_or_create(parent_category_name='I2P')

    strategic_sourcing_module, _ = Modules.objects.get_or_create(module_name='Strategic Sourcing')
    supplier_management_module, _ = Modules.objects.get_or_create(module_name='Supplier Management')
    spend_analytics_module, _ = Modules.objects.get_or_create(module_name='Spend Analytics')
    contract_management_module, _ = Modules.objects.get_or_create(module_name='Contract Management')
    e_procurement_module, _ = Modules.objects.get_or_create(module_name='e-Procurement')
    invoice_to_pay_module, _ = Modules.objects.get_or_create(module_name='Invoice-to-Pay')
    strategic_procurement_technologies_module, _ = Modules.objects.get_or_create(
        module_name='Strategic Procurement Technologies')
    procure_to_pay_module, _ = Modules.objects.get_or_create(module_name='Procure-to-Pay')
    source_to_pay_module, _ = Modules.objects.get_or_create(module_name='Source-to-Pay')
    ap_automation_module, _ = Modules.objects.get_or_create(module_name='AP Automation')

    ModulesParentCategories.objects.get_or_create(module=strategic_sourcing_module, parent_category=common_s2p_category,
                                                  primary=False)
    ModulesParentCategories.objects.get_or_create(module=strategic_sourcing_module,
                                                  parent_category=common_sourcing_sxm_category,
                                                  primary=False)
    ModulesParentCategories.objects.get_or_create(module=strategic_sourcing_module, parent_category=services_category,
                                                  primary=False)
    ModulesParentCategories.objects.get_or_create(module=strategic_sourcing_module, parent_category=sourcing_category,
                                                  primary=True)

    ModulesParentCategories.objects.get_or_create(module=supplier_management_module,
                                                  parent_category=common_s2p_category,
                                                  primary=False)
    ModulesParentCategories.objects.get_or_create(module=supplier_management_module,
                                                  parent_category=common_sourcing_sxm_category,
                                                  primary=False)
    ModulesParentCategories.objects.get_or_create(module=supplier_management_module, parent_category=services_category,
                                                  primary=False)
    ModulesParentCategories.objects.get_or_create(module=supplier_management_module, parent_category=sxm_category,
                                                  primary=True)

    ModulesParentCategories.objects.get_or_create(module=spend_analytics_module, parent_category=common_s2p_category,
                                                  primary=False)
    ModulesParentCategories.objects.get_or_create(module=spend_analytics_module, parent_category=services_category,
                                                  primary=False)
    ModulesParentCategories.objects.get_or_create(module=spend_analytics_module,
                                                  parent_category=spend_analytics_category,
                                                  primary=True)

    ModulesParentCategories.objects.get_or_create(module=contract_management_module,
                                                  parent_category=common_s2p_category,
                                                  primary=False)
    ModulesParentCategories.objects.get_or_create(module=contract_management_module, parent_category=services_category,
                                                  primary=False)
    ModulesParentCategories.objects.get_or_create(module=contract_management_module, parent_category=clm_category,
                                                  primary=True)

    ModulesParentCategories.objects.get_or_create(module=e_procurement_module, parent_category=common_s2p_category,
                                                  primary=False)
    ModulesParentCategories.objects.get_or_create(module=e_procurement_module, parent_category=services_category,
                                                  primary=False)
    ModulesParentCategories.objects.get_or_create(module=e_procurement_module, parent_category=e_procurement_category,
                                                  primary=True)

    ModulesParentCategories.objects.get_or_create(module=invoice_to_pay_module, parent_category=common_s2p_category,
                                                  primary=False)
    ModulesParentCategories.objects.get_or_create(module=invoice_to_pay_module, parent_category=services_category,
                                                  primary=False)
    ModulesParentCategories.objects.get_or_create(module=invoice_to_pay_module, parent_category=i2p_category,
                                                  primary=True)

    ModulesParentCategories.objects.get_or_create(module=strategic_procurement_technologies_module,
                                                  parent_category=common_s2p_category, primary=False)
    ModulesParentCategories.objects.get_or_create(module=strategic_procurement_technologies_module,
                                                  parent_category=common_sourcing_sxm_category, primary=False)
    ModulesParentCategories.objects.get_or_create(module=strategic_procurement_technologies_module,
                                                  parent_category=services_category,
                                                  primary=False)
    ModulesParentCategories.objects.get_or_create(module=strategic_procurement_technologies_module,
                                                  parent_category=sourcing_category,
                                                  primary=True)
    ModulesParentCategories.objects.get_or_create(module=strategic_procurement_technologies_module,
                                                  parent_category=sxm_category,
                                                  primary=False)
    ModulesParentCategories.objects.get_or_create(module=strategic_procurement_technologies_module,
                                                  parent_category=spend_analytics_category, primary=False)
    ModulesParentCategories.objects.get_or_create(module=strategic_procurement_technologies_module,
                                                  parent_category=clm_category,
                                                  primary=False)

    ModulesParentCategories.objects.get_or_create(module=procure_to_pay_module, parent_category=common_s2p_category,
                                                  primary=False)
    ModulesParentCategories.objects.get_or_create(module=procure_to_pay_module, parent_category=services_category,
                                                  primary=False)
    ModulesParentCategories.objects.get_or_create(module=procure_to_pay_module, parent_category=e_procurement_category,
                                                  primary=True)
    ModulesParentCategories.objects.get_or_create(module=procure_to_pay_module, parent_category=i2p_category,
                                                  primary=False)

    ModulesParentCategories.objects.get_or_create(module=source_to_pay_module, parent_category=common_s2p_category,
                                                  primary=False)
    ModulesParentCategories.objects.get_or_create(module=source_to_pay_module,
                                                  parent_category=common_sourcing_sxm_category,
                                                  primary=False)
    ModulesParentCategories.objects.get_or_create(module=source_to_pay_module, parent_category=services_category,
                                                  primary=False)
    ModulesParentCategories.objects.get_or_create(module=source_to_pay_module, parent_category=sourcing_category,
                                                  primary=True)
    ModulesParentCategories.objects.get_or_create(module=source_to_pay_module, parent_category=sxm_category,
                                                  primary=False)
    ModulesParentCategories.objects.get_or_create(module=source_to_pay_module, parent_category=spend_analytics_category,
                                                  primary=False)
    ModulesParentCategories.objects.get_or_create(module=source_to_pay_module, parent_category=clm_category,
                                                  primary=False)
    ModulesParentCategories.objects.get_or_create(module=source_to_pay_module, parent_category=e_procurement_category,
                                                  primary=True)
    ModulesParentCategories.objects.get_or_create(module=source_to_pay_module, parent_category=i2p_category,
                                                  primary=False)

    ModulesParentCategories.objects.get_or_create(module=ap_automation_module, parent_category=common_s2p_category,
                                                  primary=False)
    ModulesParentCategories.objects.get_or_create(module=ap_automation_module, parent_category=services_category,
                                                  primary=False)
    ModulesParentCategories.objects.get_or_create(module=ap_automation_module, parent_category=i2p_category,
                                                  primary=True)


def reverse_func(apps, schema_editor):
    ModulesParentCategories = apps.get_model('vendors', 'ModulesParentCategories')
    ModulesParentCategories.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [
        ('vendors', '0057_modulesparentcategories'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ]

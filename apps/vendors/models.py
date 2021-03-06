
from django.db import models
from simple_history.models import HistoricalRecords
from service.countries import COUNTRIES


class AnalystNotes(models.Model):
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING)
    e = models.ForeignKey('Elements', models.DO_NOTHING)
    analyst_notes = models.CharField(max_length=300, blank=True, null=True)
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING, blank=True, null=True)
    rfi = models.ForeignKey('Rfis', models.DO_NOTHING)
    timestamp = models.DateTimeField(auto_now=True)
    analyst_response = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'analyst_notes'
        unique_together = (('vendor', 'e', 'rfi', 'timestamp'),)


class AnalystsFlaggedElements(models.Model):
    """Not needed for phase 1a"""
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING)
    e = models.ForeignKey('Elements', models.DO_NOTHING)
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING)
    active = models.IntegerField(blank=True, null=True)
    rfi_id = models.IntegerField()
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'analysts_flagged_elements'
        unique_together = (('vendor', 'e', 'user', 'rfi_id', 'timestamp'),)


class AssignedPcAnalysts(models.Model):
    """Not needed for phase 1a"""
    analyst = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING)
    pc = models.ForeignKey('ParentCategories', models.DO_NOTHING)
    active = models.IntegerField()
    user_id = models.IntegerField()
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'assigned_pc_analysts'
        unique_together = (('analyst', 'pc', 'timestamp'),)


class AssignedVendorsAnalysts(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    analyst = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING, blank=True, null=True)
    pc = models.ForeignKey('ParentCategories', models.DO_NOTHING, blank=True, null=True)
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING)
    active = models.IntegerField()
    user_id = models.IntegerField()
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'assigned_vendors_analysts'
        unique_together = (('analyst', 'vendor', 'timestamp'),)


class Attachments(models.Model):
    attachment_id = models.AutoField(primary_key=True)
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING)
    filename = models.CharField(max_length=200, blank=True, null=True)
    extension = models.CharField(max_length=10, blank=True, null=True)
    path = models.CharField(max_length=500, blank=True, null=True)
    notes = models.CharField(max_length=300, blank=True, null=True)
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING, blank=True, null=True)
    rfi = models.ForeignKey('Rfis', models.DO_NOTHING)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'attachments'
        unique_together = (('attachment_id', 'rfi', 'timestamp'),)


class CIAnswers(models.Model):
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING)
    c_i_question = models.ForeignKey('CIQuestions', models.DO_NOTHING)
    answer = models.CharField(max_length=1000, blank=True, null=True)
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING)
    rfi = models.ForeignKey('Rfis', models.DO_NOTHING, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'c_i_answers'
        unique_together = (('vendor', 'c_i_question'),)


class CIQuestions(models.Model):
    c_i_questionid = models.AutoField(primary_key=True)
    question = models.CharField(max_length=500, blank=True, null=True)
    active = models.BooleanField(default=True)
    user = models.ForeignKey('c_users.CustomUser', on_delete=models.CASCADE)
    rfi = models.ForeignKey('Rfis', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'c_i_questions'
        unique_together = (('c_i_questionid', 'rfi', 'timestamp'),)


class Calendar(models.Model):
    """Not needed for phase 1a"""
    eventid = models.IntegerField(primary_key=True)
    event_name = models.CharField(max_length=45)
    rfi = models.ForeignKey('Rfis', models.DO_NOTHING, blank=True, null=True)
    date1 = models.DateTimeField(blank=True, null=True)
    date2 = models.DateTimeField()
    all = models.IntegerField()
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'calendar'


class CalendarModules(models.Model):
    """Not needed for phase 1a"""
    event = models.ForeignKey(Calendar, models.DO_NOTHING)
    m = models.ForeignKey('Modules', models.DO_NOTHING)
    active = models.IntegerField()
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING)
    timestamp = models.DateTimeField()

    class Meta:
        db_table = 'calendar_modules'
        unique_together = (('event', 'm'),)


class CalendarVendors(models.Model):
    """Not needed for phase 1a"""
    event = models.ForeignKey(Calendar, models.DO_NOTHING)
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING)
    active = models.IntegerField()
    calendar_vendors_ccol = models.CharField(max_length=45)
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'calendar_vendors'
        unique_together = (('event', 'vendor'),)


class Categories(models.Model):
    cid = models.AutoField(primary_key=True)
    pc = models.ForeignKey('ParentCategories', models.DO_NOTHING, related_name='pcat')
    category_name = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'
        unique_together = (('cid', 'timestamp'),)

    def __str__(self):
        return self.category_name


class ChartsParticipation(models.Model):
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING)
    m = models.ForeignKey('Modules', models.DO_NOTHING)
    vendor_display_name = models.CharField(max_length=45)
    participation_mode = models.IntegerField()
    customer_count = models.IntegerField(blank=True, null=True)
    display_in_chart = models.IntegerField()
    include_in_averages = models.IntegerField()
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING)
    rfi = models.ForeignKey('Rfis', models.DO_NOTHING)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'charts_participation'
        unique_together = (('vendor', 'm', 'rfi', 'timestamp'),)


class CheckCWeights100(models.Model):
    """View
       Not needed for phase 1a
    """
    m_id = models.IntegerField(blank=True, null=True)
    persona_id = models.IntegerField(blank=True, null=True)
    sum_c_weight = models.IntegerField(blank=True, null=True)
    price_score_weight = models.IntegerField(blank=True, null=True)
    sum_c_weight_price_score_weight = models.IntegerField(db_column='sum_c_weight + price_score_weight',
                                                          blank=True, null=True)  # Field renamed to remove unsuitable characters.

    class Meta:
        db_table = 'check_c_weights_100'


class CheckMissingPriceScores(models.Model):
    """View
       Not needed for phase 1a
    """
    m_id = models.IntegerField(blank=True, null=True)
    persona_id = models.IntegerField(blank=True, null=True)
    price_score_weight = models.IntegerField(blank=True, null=True)
    vendor_id = models.IntegerField(blank=True, null=True)
    partic = models.IntegerField(blank=True, null=True)
    price_score = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'check_missing_price_scores'


class CheckNormWeights100(models.Model):
    """View"""
    m_id = models.IntegerField(blank=True, null=True)
    persona_id = models.IntegerField(blank=True, null=True)
    sum_norm_weights = models.IntegerField(blank=True, null=True)
    price_score_weight = models.IntegerField(blank=True, null=True)
    sum_norm_weights_price_score_weight = models.IntegerField(db_column='sum_norm_weights + price_score_weight', blank=True, null=True)  # Field renamed to remove unsuitable characters.

    class Meta:
        db_table = 'check_norm_weights_100'


class Elements(models.Model):
    eid = models.AutoField(primary_key=True)
    s = models.ForeignKey('Subcategories', models.DO_NOTHING, related_name='sub')
    element_name = models.CharField(max_length=200)
    description = models.CharField(max_length=5000, blank=True, null=True)
    scoring_scale = models.CharField(max_length=2000, blank=True, null=True)
    e_order = models.DecimalField(max_digits=9, decimal_places=4)
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now=True)
    initialize = models.BooleanField(default=False)  # For create initialize element info at first file download

    class Meta:
        db_table = 'elements'
        unique_together = (('eid', 'timestamp'),)

    def __str__(self):
        return self.element_name


class ElementsAttachments(models.Model):
    e = models.ForeignKey('Elements', models.DO_NOTHING)
    attachment_info = models.CharField(max_length=500, blank=True, null=True)
    rfi = models.ForeignKey('Rfis', models.DO_NOTHING)
    timestamp = models.DateTimeField(auto_now=True)
    active = models.IntegerField(blank=True, null=True)
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING, blank=True, null=True)
    vendor_response = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'elements_attachments'
        unique_together = (('e', 'vendor', 'rfi', 'timestamp'),)


class LogTrail(models.Model):
    log_row_id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=45, blank=True, null=True)
    successful = models.BooleanField(default=True)
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING)
    ip = models.CharField(max_length=15, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'log_trail'


class ModuleElements(models.Model):
    m = models.ForeignKey('Modules', models.DO_NOTHING)
    e = models.ForeignKey(Elements, models.DO_NOTHING)
    active = models.BooleanField(blank=True, null=True, default=True)
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING, blank=True, null=True)
    rfi = models.ForeignKey('Rfis', models.DO_NOTHING)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'module_elements'
        unique_together = (('m', 'e', 'rfi', 'timestamp'),)


class ModulePersonas(models.Model):
    """Not needed for phase 1a"""
    m = models.ForeignKey('Modules', models.DO_NOTHING)
    persona = models.ForeignKey('Personas', models.DO_NOTHING)
    price_score_weight = models.DecimalField(max_digits=5, decimal_places=3)
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING)
    rfi = models.ForeignKey('Rfis', models.DO_NOTHING)
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'module_personas'
        unique_together = (('m', 'persona', 'rfi'),)


class Modules(models.Model):
    MODULES_NAME = (
                    ("Strategic Sourcing", "Strategic Sourcing"),
                    ("Supplier Management", "Supplier Management"),
                    ("Spend Analytics", "Spend Analytics"),
                    ("Contract Management", "Contract Management"),
                    ("e-Procurement", "e-Procurement"),
                    ("Invoice-to-Pay", "Invoice-to-Pay"),
                    ("Strategic Procurement Technologies", "Strategic Procurement Technologies"),
                    ("Procure-to-Pay", "Procure-to-Pay"),
                    ("Source-to-Pay", "Source-to-Pay"),
                    ("AP Automation", "AP Automation"),
                    )
    mid = models.AutoField(primary_key=True)
    module_name = models.CharField(max_length=50, choices=MODULES_NAME, unique=True)
    active = models.BooleanField(default=True)
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now=True)
    parent_categories = models.ManyToManyField('ParentCategories', through='ModulesParentCategories',
                                               related_name='parent_categories')

    class Meta:
        db_table = 'modules'
        unique_together = (('mid', 'timestamp'),)

    def __str__(self):
        return "{} id: {}".format(self.module_name, self.mid)


class MsSmScores(models.Model):
    """View"""
    module_name = models.IntegerField(blank=True, null=True)
    persona_name = models.IntegerField(blank=True, null=True)
    vendor_name = models.IntegerField(blank=True, null=True)
    sm_score = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'ms_sm_scores'


class NormEWeights(models.Model):
    """View
       Not needed for phase 1a
    """
    m_id = models.IntegerField(blank=True, null=True)
    persona_id = models.IntegerField(blank=True, null=True)
    e_id = models.IntegerField(blank=True, null=True)
    c_id = models.IntegerField(blank=True, null=True)
    sum_e_weight_by_c = models.IntegerField(blank=True, null=True)
    c_weight = models.IntegerField(blank=True, null=True)
    norm_weight = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'norm_e_weights'


class ParentCategories(models.Model):
    PC = (
        ("COMMON S2P", "COMMON S2P"),
        ("COMMON SOURCING – SXM", "COMMON SOURCING – SXM"),
        ("SERVICES", "SERVICES"),
        ("SOURCING", "SOURCING"),
        ("SXM", "SXM"),
        ("Spend Analytics", "Spend Analytics"),
        ("CLM", "CLM"),
        ("eProcurement", "eProcurement"),
        ("I2P", "I2P"),

    )
    pcid = models.AutoField(primary_key=True)
    parent_category_name = models.CharField(max_length=45, choices=PC, unique=True)
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'parent_categories'
        unique_together = (('pcid', 'timestamp'),)

    def __str__(self):
        return self.parent_category_name


class Personas(models.Model):
    """Not needed for phase 1a"""
    personaid = models.AutoField(primary_key=True)
    persona_name = models.CharField(max_length=45, blank=True, null=True)
    active = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'personas'
        unique_together = (('personaid', 'timestamp'),)


class PriceScores(models.Model):
    """Not needed for phase 1a"""
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING)
    m = models.ForeignKey('Modules', models.DO_NOTHING)
    persona = models.ForeignKey('Personas', models.DO_NOTHING)
    price_score = models.DecimalField(max_digits=4, decimal_places=3, blank=True, null=True)
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING)
    rfi = models.ForeignKey('Rfis', models.DO_NOTHING)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'price_scores'
        unique_together = (('vendor', 'm', 'persona', 'rfi', 'timestamp'),)


class ReferenceModules(models.Model):
    """Not needed for phase 1a"""
    reference = models.ForeignKey('References', models.DO_NOTHING)
    m = models.ForeignKey(Modules, models.DO_NOTHING)
    active = models.IntegerField()
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING)
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'reference_modules'
        unique_together = (('reference', 'm'),)


class References(models.Model):
    """Not needed for phase 1a"""
    reference_id = models.AutoField(primary_key=True)
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING, blank=True, null=True)
    datetime = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=45, blank=True, null=True)
    email = models.CharField(max_length=100, blank=True, null=True)
    company = models.CharField(max_length=45, blank=True, null=True)
    rfi = models.ForeignKey('Rfis', models.DO_NOTHING, blank=True, null=True)
    ref_status_id = models.IntegerField(blank=True, null=True)
    internal_comments = models.CharField(max_length=100, blank=True, null=True)
    provider_public = models.CharField(max_length=10, blank=True, null=True)
    original_vendor_id = models.IntegerField(blank=True, null=True)
    active = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING)
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'references'


class RfiParticipation(models.Model):
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING, related_name='to_vendor')
    m = models.ForeignKey('Modules', models.DO_NOTHING, related_name='to_modules')
    active = models.BooleanField(default=False)
    user_id = models.IntegerField(null=True, blank=True)
    rfi = models.ForeignKey('Rfis', related_name='to_rfi', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rfi_participation'
        unique_together = (('vendor', 'm', 'rfi',),)

    def __str__(self):
        return "{} is {} for {}".format(self.m.module_name, self.active, self.vendor.vendor_name)


class RfiParticipationStatus(models.Model):
    STATUS_NAME = (
                    ("Invited", "Invited"), ("Accepted", "Accepted"),
                    ("Declined", "Declined"), ("Created", "Created"),
                    ("Outstanding", "Outstanding"), ("Received", "Received"),
                    ("Scored", "Scored"), ("Closed", "Closed"),)

    status = models.CharField(max_length=50, choices=STATUS_NAME, default='Invited')
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING, related_name='to_vendor_status')
    rfi = models.ForeignKey('Rfis', models.DO_NOTHING, related_name='to_rfis_status')
    pc = models.ForeignKey(ParentCategories, models.DO_NOTHING, blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now=True)
    last_vendor_response = models.IntegerField(default=0)
    last_analyst_response = models.IntegerField(default=0)

    class Meta:
        db_table = 'rfi_participation_status'
        unique_together = (('vendor', 'rfi', 'timestamp', 'pc'),)

    def __str__(self):
        return f"{self.vendor} - {self.rfi} - {self.pc}"


class Rfis(models.Model):
    RFI_STATUS = (
                    ("Created", "Created"),
                    ("Opened", "Opened"),
                    ("Issued", "Issued"),
                    ("Closed", "Closed")
                 )
    rfi_status = models.CharField(max_length=50, choices=RFI_STATUS, default="Created")
    rfiid = models.CharField(max_length=4, primary_key=True)
    active = models.BooleanField(default=True)
    issue_datetime = models.DateTimeField(blank=True, null=True)
    open_datetime = models.DateTimeField(blank=True, null=True)
    close_datetime = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rfis'
        unique_together = (('rfiid', 'timestamp'),)

    def __str__(self):
        return self.rfiid


class SelfDescriptions(models.Model):
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING)
    e = models.ForeignKey(Elements, models.DO_NOTHING)
    self_description = models.CharField(max_length=2500, blank=True, null=True)
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING, blank=True, null=True)
    rfi = models.ForeignKey(Rfis, models.DO_NOTHING)
    timestamp = models.DateTimeField(auto_now=True)
    vendor_response = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'self_descriptions'
        unique_together = (('vendor', 'e', 'rfi', 'timestamp'),)


class SelfScores(models.Model):
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING)
    e = models.ForeignKey(Elements, models.DO_NOTHING, related_name='self_score')
    self_score = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True)
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING, blank=True, null=True)
    rfi = models.ForeignKey(Rfis, models.DO_NOTHING)
    timestamp = models.DateTimeField(auto_now=True)
    vendor_response = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'self_scores'
        unique_together = (('vendor', 'e', 'rfi', 'timestamp'),)


class Shifts(models.Model):
    m = models.ForeignKey('Modules', models.DO_NOTHING)
    persona = models.ForeignKey(Personas, models.DO_NOTHING)
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING)
    sm_score_partic_2 = models.DecimalField(max_digits=3, decimal_places=2)
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING, blank=True, null=True)
    rfi = models.ForeignKey(Rfis, models.DO_NOTHING)
    timestamp = models.DateTimeField()

    class Meta:
        db_table = 'shifts'
        unique_together = (('m', 'persona', 'vendor', 'rfi', 'timestamp'),)


class SmScores(models.Model):
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING)
    e = models.ForeignKey('Elements', models.DO_NOTHING)
    sm_score = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True)
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING, blank=True, null=True)
    rfi = models.ForeignKey(Rfis, models.DO_NOTHING)
    timestamp = models.DateTimeField(auto_now=True)
    analyst_response = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'sm_scores'
        unique_together = (('vendor', 'e', 'rfi', 'timestamp'),)


class SmScoresPartic1(models.Model):
    """View
       Not needed for phase 1a
    """
    m_id = models.IntegerField(blank=True, null=True)
    persona_id = models.IntegerField(blank=True, null=True)
    vendor_id = models.IntegerField(blank=True, null=True)
    sm_score_partic_1 = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'sm_scores_partic_1'


class Subcategories(models.Model):
    sid = models.AutoField(primary_key=True)
    c = models.ForeignKey('Categories', models.DO_NOTHING, related_name='cat')
    subcategory_name = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'subcategories'
        unique_together = (('sid', 'timestamp'),)

    def __str__(self):
        return self.subcategory_name


class SumVpScores(models.Model):
    """View
       Not needed for phase 1a
    """
    vendor_id = models.IntegerField(blank=True, null=True)
    m_id = models.IntegerField(blank=True, null=True)
    persona_id = models.IntegerField(blank=True, null=True)
    sum_vp_score = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'sum_vp_scores'


class SurveyAnswers(models.Model):
    """Not needed for phase 1a"""
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING)
    reference = models.ForeignKey('References', models.DO_NOTHING, blank=True, null=True)
    question = models.ForeignKey('SurveyQuestions', models.DO_NOTHING)
    answer = models.CharField(max_length=1000, blank=True, null=True)
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING)
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'survey_answers'
        unique_together = (('vendor', 'question'),)


class SurveyQuestions(models.Model):
    """Not needed for phase 1a"""
    questionid = models.AutoField(primary_key=True)
    statement = models.CharField(max_length=500)
    active = models.IntegerField()
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING)
    rfi = models.ForeignKey(Rfis, models.DO_NOTHING)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'survey_questions'
        unique_together = (('questionid', 'timestamp', 'rfi'),)


class UserAssignedSubcategories(models.Model):
    """Not needed for phase 1a"""
    user_to_assign = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING, related_name='user_to_assign')
    s = models.ForeignKey(Subcategories, models.DO_NOTHING)
    active = models.IntegerField()
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_assigned_subcategories'
        unique_together = (('user_to_assign', 's', 'timestamp'),)


class UserRoles(models.Model):
    """Not needed for phase 1a"""
    user_roleid = models.AutoField(primary_key=True)
    user_role = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        db_table = 'user_roles'


class VendorContacts(models.Model):
    contact_id = models.AutoField(primary_key=True)
    vendor = models.ForeignKey('Vendors', related_name='contacts', on_delete=models.CASCADE)
    contact_name = models.CharField(max_length=45, blank=True, null=True)
    email = models.CharField(max_length=80, blank=True, null=True)
    phone = models.CharField(max_length=45, blank=True, null=True)
    primary = models.BooleanField(default=True)

    class Meta:
        db_table = 'vendor_contacts'

    def __str__(self):
        return '{}: {}'.format(self.contact_name, self.vendor.vendor_name)


class VendorModuleNames(models.Model):
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING, related_name='vendor_modules')
    module = models.ForeignKey('Modules', models.DO_NOTHING)
    vendor_name = models.CharField(max_length=45)
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'vendor_module_names'
        unique_together = (('vendor', 'module'),)

    def __str__(self):
        return '{} - {}'.format(self.module, self.vendor_name)


class Vendors(models.Model):
    COUNTRY_CHOICES = tuple(COUNTRIES)

    vendorid = models.AutoField(primary_key=True)
    vendor_name = models.CharField(max_length=45, unique=True, error_messages={'unique': "Vendor already exists"})
    country = models.CharField(max_length=145, choices=COUNTRY_CHOICES)
    office = models.CharField(max_length=145, blank=True, null=True)
    abr_date = models.DateField(blank=True, null=True)
    nda = models.DateField(blank=True, null=True)
    consent = models.DateField(blank=True, null=True)
    parent = models.ForeignKey('Vendors', models.DO_NOTHING, blank=True, null=True)
    active = models.BooleanField(default=False)
    user_id = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords(excluded_fields=['country', 'office', 'abr_date', 'nda', 'consent',
                                                 'parent', 'active', 'user_id', 'timestamp'])

    class Meta:
        db_table = 'vendors'
        unique_together = (('vendorid', 'timestamp'),)

    def __str__(self):
        return self.vendor_name

    def save_without_historical_record(self, *args, **kwargs):
        self.skip_history_when_saving = True
        try:
            ret = self.save(*args, **kwargs)
        finally:
            del self.skip_history_when_saving
        return ret


class VpScores(models.Model):
    """View
       Not needed for phase 1a
    """
    vendor_id = models.IntegerField(blank=True, null=True)
    m_id = models.IntegerField(blank=True, null=True)
    persona_id = models.IntegerField(blank=True, null=True)
    e_id = models.IntegerField(blank=True, null=True)
    vp_score = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'vp_scores'


class WeightsCategories(models.Model):
    m = models.ForeignKey('Modules', models.DO_NOTHING)
    persona = models.ForeignKey('Personas', models.DO_NOTHING)
    c = models.ForeignKey('Categories', models.DO_NOTHING)
    c_weight = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING)
    rfi = models.ForeignKey(Rfis, models.DO_NOTHING)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'weights_categories'
        unique_together = (('m', 'persona', 'c', 'rfi', 'timestamp'),)


class WeightsElements(models.Model):
    """Not needed for phase 1a"""
    m = models.ForeignKey(Modules, models.DO_NOTHING)
    persona = models.ForeignKey(Personas, models.DO_NOTHING)
    e = models.ForeignKey(Elements, models.DO_NOTHING)
    e_weight = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING)
    rfi = models.ForeignKey('Rfis', models.DO_NOTHING)
    timestamp = models.DateTimeField()

    class Meta:
        db_table = 'weights_elements'
        unique_together = (('m', 'persona', 'e', 'rfi', 'timestamp'),)


class WeightsSurveyQuestions(models.Model):
    """Not needed for phase 1a"""
    persona = models.ForeignKey(Personas, models.DO_NOTHING)
    m = models.ForeignKey(Modules, models.DO_NOTHING)
    question = models.ForeignKey(SurveyQuestions, models.DO_NOTHING)
    weight = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING)
    rfi = models.ForeignKey('Rfis', models.DO_NOTHING, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'weights_survey_questions'
        unique_together = (('persona', 'm', 'question'),)


class FinalOutputData(models.Model):
    rfi = models.ForeignKey('Rfis', on_delete=models.CASCADE)
    m = models.OneToOneField('Modules', models.DO_NOTHING)
    persona = models.ForeignKey('Personas', models.DO_NOTHING)
    vendor = models.ForeignKey('Vendors', on_delete=models.CASCADE)
    bubble_size = models.IntegerField(blank=True, null=True)
    number_of_refs = models.IntegerField(blank=True, null=True)
    customer_score = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    sm_score = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    displayed = models.IntegerField(blank=True, null=True)
    version = models.IntegerField(blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'final_output_data'
        unique_together = (('m', 'persona', 'vendor', 'rfi'),)


class CompanyGeneralInfoQuestion(models.Model):
    questionid = models.AutoField(primary_key=True)
    question = models.CharField(max_length=512)
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING, blank=True, null=True)
    rfi = models.ForeignKey(Rfis, models.DO_NOTHING)
    timestamp = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'company_info__questions'


class CompanyGeneralInfoAnswers(models.Model):
    answerid = models.AutoField(primary_key=True)
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING)
    question = models.ForeignKey('CompanyGeneralInfoQuestion', models.DO_NOTHING, related_name='answer_to_question')
    answer = models.CharField(max_length=4096, blank=True, null=True)
    user = models.ForeignKey('c_users.CustomUser', models.DO_NOTHING, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now=True)
    scoring = models.IntegerField(default=0)

    class Meta:
        db_table = 'company_info_answers'


class ModulesParentCategories(models.Model):
    module = models.ForeignKey('Modules', on_delete=models.CASCADE)
    parent_category = models.ForeignKey('ParentCategories', on_delete=models.CASCADE)
    primary = models.BooleanField(default=False)

    class Meta:
        unique_together = (('module', 'parent_category'),)

    def __str__(self):
        return '{} - {}'.format(self.parent_category.parent_category_name, self.module.module_name)

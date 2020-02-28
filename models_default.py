# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AnalystNotes(models.Model):
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING, primary_key=True)
    e = models.ForeignKey('Elements', models.DO_NOTHING)
    analyst_notes = models.CharField(max_length=300, blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    rfi = models.ForeignKey('Rfis', models.DO_NOTHING)
    timestamp = models.DateTimeField()
    analyst_response = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'analyst_notes'
        unique_together = (('vendor', 'e', 'rfi', 'timestamp'),)


class AnalystsFlaggedElements(models.Model):
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING, primary_key=True)
    e = models.ForeignKey('Elements', models.DO_NOTHING)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    active = models.IntegerField(blank=True, null=True)
    rfi_id = models.IntegerField()
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'analysts_flagged_elements'
        unique_together = (('vendor', 'e', 'user', 'rfi_id', 'timestamp'),)


class AssignedPcAnalysts(models.Model):
    analyst = models.ForeignKey('Users', models.DO_NOTHING, primary_key=True)
    pc = models.ForeignKey('ParentCategories', models.DO_NOTHING)
    active = models.IntegerField()
    user_id = models.IntegerField()
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'assigned_pc_analysts'
        unique_together = (('analyst', 'pc', 'timestamp'),)


class AssignedVendorsAnalysts(models.Model):
    analyst = models.ForeignKey('Users', models.DO_NOTHING, primary_key=True)
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING)
    active = models.IntegerField()
    user_id = models.IntegerField()
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'assigned_vendors_analysts'
        unique_together = (('analyst', 'vendor', 'timestamp'),)


class Attachments(models.Model):
    attachment_id = models.AutoField(primary_key=True)
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING)
    filename = models.CharField(max_length=200, blank=True, null=True)
    extension = models.CharField(max_length=10, blank=True, null=True)
    path = models.CharField(max_length=500, blank=True, null=True)
    notes = models.CharField(max_length=300, blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    rfi = models.ForeignKey('Rfis', models.DO_NOTHING)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'attachments'
        unique_together = (('attachment_id', 'rfi', 'timestamp'),)


class CIAnswers(models.Model):
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING, primary_key=True)
    c_i_question = models.ForeignKey('CIQuestions', models.DO_NOTHING)
    answer = models.CharField(max_length=1000, blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    rfi = models.ForeignKey('Rfis', models.DO_NOTHING, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'c_i_answers'
        unique_together = (('vendor', 'c_i_question'),)


class CIQuestions(models.Model):
    c_i_questionid = models.IntegerField(primary_key=True)
    question = models.CharField(max_length=500, blank=True, null=True)
    active = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    rfi = models.ForeignKey('Rfis', models.DO_NOTHING)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'c_i_questions'
        unique_together = (('c_i_questionid', 'rfi', 'timestamp'),)


class Calendar(models.Model):
    eventid = models.IntegerField(primary_key=True)
    event_name = models.CharField(max_length=45)
    rfi = models.ForeignKey('Rfis', models.DO_NOTHING, blank=True, null=True)
    date1 = models.DateTimeField(blank=True, null=True)
    date2 = models.DateTimeField()
    all = models.IntegerField()
    user = models.ForeignKey('Users', models.DO_NOTHING)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'calendar'


class CalendarModules(models.Model):
    event = models.ForeignKey(Calendar, models.DO_NOTHING, primary_key=True)
    m = models.ForeignKey('Modules', models.DO_NOTHING)
    active = models.IntegerField()
    user = models.ForeignKey('Users', models.DO_NOTHING)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'calendar_modules'
        unique_together = (('event', 'm'),)


class CalendarVendors(models.Model):
    event = models.ForeignKey(Calendar, models.DO_NOTHING, primary_key=True)
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING)
    active = models.IntegerField()
    calendar_vendors_ccol = models.CharField(max_length=45)
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'calendar_vendors'
        unique_together = (('event', 'vendor'),)


class Categories(models.Model):
    cid = models.AutoField(primary_key=True)
    pc = models.ForeignKey('ParentCategories', models.DO_NOTHING)
    category_name = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'categories'
        unique_together = (('cid', 'timestamp'),)


class ChartsParticipation(models.Model):
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING, primary_key=True)
    m = models.ForeignKey('Modules', models.DO_NOTHING)
    vendor_display_name = models.CharField(max_length=45)
    participation_mode = models.IntegerField()
    customer_count = models.IntegerField(blank=True, null=True)
    display_in_chart = models.IntegerField()
    include_in_averages = models.IntegerField()
    user = models.ForeignKey('Users', models.DO_NOTHING)
    rfi = models.ForeignKey('Rfis', models.DO_NOTHING)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'charts_participation'
        unique_together = (('vendor', 'm', 'rfi', 'timestamp'),)


class CheckCWeights100(models.Model):
    m_id = models.IntegerField(blank=True, null=True)
    persona_id = models.IntegerField(blank=True, null=True)
    sum_c_weight = models.IntegerField(blank=True, null=True)
    price_score_weight = models.IntegerField(blank=True, null=True)
    sum_c_weight_price_score_weight = models.IntegerField(db_column='sum_c_weight + price_score_weight', blank=True, null=True)  # Field renamed to remove unsuitable characters.

    class Meta:
        managed = False
        db_table = 'check_c_weights_100'


class CheckMissingPriceScores(models.Model):
    m_id = models.IntegerField(blank=True, null=True)
    persona_id = models.IntegerField(blank=True, null=True)
    price_score_weight = models.IntegerField(blank=True, null=True)
    vendor_id = models.IntegerField(blank=True, null=True)
    partic = models.IntegerField(blank=True, null=True)
    price_score = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'check_missing_price_scores'


class CheckNormWeights100(models.Model):
    m_id = models.IntegerField(blank=True, null=True)
    persona_id = models.IntegerField(blank=True, null=True)
    sum_norm_weights = models.IntegerField(blank=True, null=True)
    price_score_weight = models.IntegerField(blank=True, null=True)
    sum_norm_weights_price_score_weight = models.IntegerField(db_column='sum_norm_weights + price_score_weight', blank=True, null=True)  # Field renamed to remove unsuitable characters.

    class Meta:
        managed = False
        db_table = 'check_norm_weights_100'


class Elements(models.Model):
    eid = models.AutoField(primary_key=True)
    s = models.ForeignKey('Subcategories', models.DO_NOTHING)
    element_name = models.CharField(max_length=200)
    description = models.CharField(max_length=5000, blank=True, null=True)
    scoring_scale = models.CharField(max_length=2000, blank=True, null=True)
    e_order = models.DecimalField(max_digits=9, decimal_places=4)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'elements'
        unique_together = (('eid', 'timestamp'),)


class ElementsAttachments(models.Model):
    e = models.ForeignKey(Elements, models.DO_NOTHING, primary_key=True)
    attachment = models.ForeignKey(Attachments, models.DO_NOTHING)
    rfi = models.ForeignKey('Rfis', models.DO_NOTHING)
    timestamp = models.DateTimeField()
    active = models.IntegerField()
    vendor_response = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'elements_attachments'
        unique_together = (('e', 'attachment', 'rfi', 'timestamp'),)


class LogTrail(models.Model):
    log_row_id = models.AutoField(primary_key=True)
    email = models.CharField(max_length=45, blank=True, null=True)
    succesful = models.IntegerField()
    user = models.ForeignKey('Users', models.DO_NOTHING)
    ip = models.CharField(max_length=15, blank=True, null=True)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'log_trail'


class ModuleElements(models.Model):
    m = models.ForeignKey('Modules', models.DO_NOTHING, primary_key=True)
    e = models.ForeignKey(Elements, models.DO_NOTHING)
    active = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    rfi = models.ForeignKey('Rfis', models.DO_NOTHING)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'module_elements'
        unique_together = (('m', 'e', 'rfi', 'timestamp'),)


class ModulePersonas(models.Model):
    m = models.ForeignKey('Modules', models.DO_NOTHING, primary_key=True)
    persona = models.ForeignKey('Personas', models.DO_NOTHING)
    price_score_weight = models.DecimalField(max_digits=5, decimal_places=3)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    rfi = models.ForeignKey('Rfis', models.DO_NOTHING)
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'module_personas'
        unique_together = (('m', 'persona', 'rfi'),)


class Modules(models.Model):
    mid = models.AutoField(primary_key=True)
    module_name = models.CharField(max_length=50)
    active = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'modules'
        unique_together = (('mid', 'timestamp'),)


class MsSmScores(models.Model):
    module_name = models.IntegerField(blank=True, null=True)
    persona_name = models.IntegerField(blank=True, null=True)
    vendor_name = models.IntegerField(blank=True, null=True)
    sm_score = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ms_sm_scores'


class NormEWeights(models.Model):
    m_id = models.IntegerField(blank=True, null=True)
    persona_id = models.IntegerField(blank=True, null=True)
    e_id = models.IntegerField(blank=True, null=True)
    c_id = models.IntegerField(blank=True, null=True)
    sum_e_weight_by_c = models.IntegerField(blank=True, null=True)
    c_weight = models.IntegerField(blank=True, null=True)
    norm_weight = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'norm_e_weights'


class ParentCategories(models.Model):
    pcid = models.AutoField(primary_key=True)
    parent_category_name = models.CharField(max_length=45, blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'parent_categories'
        unique_together = (('pcid', 'timestamp'),)


class Personas(models.Model):
    personaid = models.IntegerField(primary_key=True)
    persona_name = models.CharField(max_length=45, blank=True, null=True)
    active = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'personas'
        unique_together = (('personaid', 'timestamp'),)


class PriceScores(models.Model):
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING, primary_key=True)
    m = models.ForeignKey(Modules, models.DO_NOTHING)
    persona = models.ForeignKey(Personas, models.DO_NOTHING)
    price_score = models.DecimalField(max_digits=4, decimal_places=3, blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    rfi = models.ForeignKey('Rfis', models.DO_NOTHING)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'price_scores'
        unique_together = (('vendor', 'm', 'persona', 'rfi', 'timestamp'),)


class ReferenceModules(models.Model):
    reference = models.ForeignKey('References', models.DO_NOTHING, primary_key=True)
    m = models.ForeignKey(Modules, models.DO_NOTHING)
    active = models.IntegerField()
    user = models.ForeignKey('Users', models.DO_NOTHING)
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'reference_modules'
        unique_together = (('reference', 'm'),)


class References(models.Model):
    reference_id = models.IntegerField(primary_key=True)
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
    user = models.ForeignKey('Users', models.DO_NOTHING)
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'references'


class RfiParticipation(models.Model):
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING, primary_key=True)
    m = models.ForeignKey(Modules, models.DO_NOTHING)
    active = models.IntegerField()
    user_id = models.IntegerField()
    rfi = models.ForeignKey('Rfis', models.DO_NOTHING)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'rfi_participation'
        unique_together = (('vendor', 'm', 'rfi', 'timestamp'),)


class RfiParticipationStatus(models.Model):
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING, primary_key=True)
    rfi = models.ForeignKey('Rfis', models.DO_NOTHING)
    pc = models.ForeignKey(ParentCategories, models.DO_NOTHING)
    user_id = models.IntegerField()
    timestamp = models.DateTimeField()
    last_vendor_response = models.IntegerField(blank=True, null=True)
    last_analyst_response = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'rfi_participation_status'
        unique_together = (('vendor', 'rfi', 'timestamp', 'pc'),)


class Rfis(models.Model):
    rfiid = models.IntegerField(primary_key=True)
    active = models.IntegerField()
    issue_datetime = models.DateTimeField(blank=True, null=True)
    open_datetime = models.DateTimeField(blank=True, null=True)
    close_datetime = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'rfis'
        unique_together = (('rfiid', 'timestamp'),)


class SelfDescriptions(models.Model):
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING, primary_key=True)
    e = models.ForeignKey(Elements, models.DO_NOTHING)
    self_description = models.CharField(max_length=2500, blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    rfi = models.ForeignKey(Rfis, models.DO_NOTHING)
    timestamp = models.DateTimeField()
    vendor_response = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'self_descriptions'
        unique_together = (('vendor', 'e', 'rfi', 'timestamp'),)


class SelfScores(models.Model):
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING, primary_key=True)
    e = models.ForeignKey(Elements, models.DO_NOTHING)
    self_score = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    rfi = models.ForeignKey(Rfis, models.DO_NOTHING)
    timestamp = models.DateTimeField()
    vendor_response = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'self_scores'
        unique_together = (('vendor', 'e', 'rfi', 'timestamp'),)


class Shifts(models.Model):
    m = models.ForeignKey(Modules, models.DO_NOTHING, primary_key=True)
    persona = models.ForeignKey(Personas, models.DO_NOTHING)
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING)
    sm_score_partic_2 = models.DecimalField(max_digits=3, decimal_places=2)
    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    rfi = models.ForeignKey(Rfis, models.DO_NOTHING)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'shifts'
        unique_together = (('m', 'persona', 'vendor', 'rfi', 'timestamp'),)


class SmScores(models.Model):
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING, primary_key=True)
    e = models.ForeignKey(Elements, models.DO_NOTHING)
    sm_score = models.DecimalField(max_digits=2, decimal_places=1, blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    rfi = models.ForeignKey(Rfis, models.DO_NOTHING)
    timestamp = models.DateTimeField()
    analyst_response = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sm_scores'
        unique_together = (('vendor', 'e', 'rfi', 'timestamp'),)


class SmScoresPartic1(models.Model):
    m_id = models.IntegerField(blank=True, null=True)
    persona_id = models.IntegerField(blank=True, null=True)
    vendor_id = models.IntegerField(blank=True, null=True)
    sm_score_partic_1 = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sm_scores_partic_1'


class Subcategories(models.Model):
    sid = models.AutoField(primary_key=True)
    c = models.ForeignKey(Categories, models.DO_NOTHING)
    subcategory_name = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'subcategories'
        unique_together = (('sid', 'timestamp'),)


class SumVpScores(models.Model):
    vendor_id = models.IntegerField(blank=True, null=True)
    m_id = models.IntegerField(blank=True, null=True)
    persona_id = models.IntegerField(blank=True, null=True)
    sum_vp_score = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sum_vp_scores'


class SurveyAnswers(models.Model):
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING, primary_key=True)
    reference = models.ForeignKey(References, models.DO_NOTHING, blank=True, null=True)
    question = models.ForeignKey('SurveyQuestions', models.DO_NOTHING)
    answer = models.CharField(max_length=1000, blank=True, null=True)
    user = models.ForeignKey('Users', models.DO_NOTHING)
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'survey_answers'
        unique_together = (('vendor', 'question'),)


class SurveyQuestions(models.Model):
    questionid = models.IntegerField(primary_key=True)
    statement = models.CharField(max_length=500)
    active = models.IntegerField()
    user = models.ForeignKey('Users', models.DO_NOTHING)
    rfi = models.ForeignKey(Rfis, models.DO_NOTHING)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'survey_questions'
        unique_together = (('questionid', 'timestamp', 'rfi'),)


class UserAssignedSubcategories(models.Model):
    user_to_assign = models.ForeignKey('Users', models.DO_NOTHING, primary_key=True)
    s = models.ForeignKey(Subcategories, models.DO_NOTHING)
    active = models.IntegerField()
    user = models.ForeignKey('Users', models.DO_NOTHING)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'user_assigned_subcategories'
        unique_together = (('user_to_assign', 's', 'timestamp'),)


class UserRoles(models.Model):
    user_roleid = models.IntegerField(primary_key=True)
    user_role = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'user_roles'


class Users(models.Model):
    userid = models.AutoField(primary_key=True)
    email = models.CharField(max_length=80)
    user_role = models.ForeignKey(UserRoles, models.DO_NOTHING, blank=True, null=True)
    assigned_vendor = models.ForeignKey('Vendors', models.DO_NOTHING, blank=True, null=True)
    password = models.CharField(max_length=45)
    active = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey('self', models.DO_NOTHING)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'users'
        unique_together = (('userid', 'timestamp'),)


class VendorContacts(models.Model):
    contact_id = models.IntegerField(primary_key=True)
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING)
    contact_name = models.CharField(max_length=45, blank=True, null=True)
    email = models.CharField(max_length=80, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vendor_contacts'


class VendorModuleNames(models.Model):
    vendor = models.ForeignKey('Vendors', models.DO_NOTHING, primary_key=True)
    module = models.ForeignKey(Modules, models.DO_NOTHING)
    vendor_name = models.CharField(max_length=45)
    user = models.ForeignKey(Users, models.DO_NOTHING)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'vendor_module_names'
        unique_together = (('vendor', 'module'),)


class Vendors(models.Model):
    vendorid = models.AutoField(primary_key=True)
    vendor_name = models.CharField(max_length=45)
    nda = models.IntegerField(blank=True, null=True)
    consent = models.IntegerField(blank=True, null=True)
    active = models.IntegerField()
    user_id = models.IntegerField()
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'vendors'
        unique_together = (('vendorid', 'timestamp'),)


class VpScores(models.Model):
    vendor_id = models.IntegerField(blank=True, null=True)
    m_id = models.IntegerField(blank=True, null=True)
    persona_id = models.IntegerField(blank=True, null=True)
    e_id = models.IntegerField(blank=True, null=True)
    vp_score = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'vp_scores'


class WeightsCategories(models.Model):
    m = models.ForeignKey(Modules, models.DO_NOTHING, primary_key=True)
    persona = models.ForeignKey(Personas, models.DO_NOTHING)
    c = models.ForeignKey(Categories, models.DO_NOTHING)
    c_weight = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
    user = models.ForeignKey(Users, models.DO_NOTHING)
    rfi = models.ForeignKey(Rfis, models.DO_NOTHING)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'weights_categories'
        unique_together = (('m', 'persona', 'c', 'rfi', 'timestamp'),)


class WeightsElements(models.Model):
    m = models.ForeignKey(Modules, models.DO_NOTHING, primary_key=True)
    persona = models.ForeignKey(Personas, models.DO_NOTHING)
    e = models.ForeignKey(Elements, models.DO_NOTHING)
    e_weight = models.DecimalField(max_digits=5, decimal_places=3, blank=True, null=True)
    user = models.ForeignKey(Users, models.DO_NOTHING)
    rfi = models.ForeignKey(Rfis, models.DO_NOTHING)
    timestamp = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'weights_elements'
        unique_together = (('m', 'persona', 'e', 'rfi', 'timestamp'),)


class WeightsSurveyQuestions(models.Model):
    persona = models.ForeignKey(Personas, models.DO_NOTHING, primary_key=True)
    m = models.ForeignKey(Modules, models.DO_NOTHING)
    question = models.ForeignKey(SurveyQuestions, models.DO_NOTHING)
    weight = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    user = models.ForeignKey(Users, models.DO_NOTHING)
    rfi = models.ForeignKey(Rfis, models.DO_NOTHING, blank=True, null=True)
    timestamp = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'weights_survey_questions'
        unique_together = (('persona', 'm', 'question'),)

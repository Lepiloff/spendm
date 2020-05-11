import re
from datetime import date
import datetime

from django.db.models import F
from django.db import DataError
from django.shortcuts import get_object_or_404
from django.core.validators import RegexValidator

from rest_framework import serializers

from apps.c_users.models import CustomUser
from .models import Vendors, VendorContacts, VendorModuleNames, Modules, Rfis, RfiParticipation, \
    Elements, Subcategories, Categories, ParentCategories, SelfDescriptions, SelfScores, \
    AnalystNotes, SmScores, ModuleElements, Attachments, ElementsAttachments, RfiParticipationStatus , \
    CompanyGeneralInfoQuestion, CompanyGeneralInfoAnswers, AssignedVendorsAnalysts


class AnalystSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignedVendorsAnalysts
        fields = ('pk', )


class VendorToFrontSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendors
        fields = ('pk', 'vendor_name')


class VendorActiveToFrontSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendors
        fields = ('pk', 'vendor_name')


class VendorContactSerializer(serializers.ModelSerializer):
    email = serializers.CharField(validators=[RegexValidator(regex=r'[^@]+@[^\.]+\..+',
                                                             message='Enter valid email address')], allow_blank=True)

    class Meta:
        model = VendorContacts
        fields = ('contact_id',
                  'contact_name',
                  'phone',
                  'email',
                  'primary',
                    )
        read_only_fields = ('contact_id', )

    def validate_email(self, value):
        # Check if email exist in active vendor and raise exception
        if value != "":
            exist_contact = VendorContacts.objects.filter(email=value).filter(vendor__active=True)
            if exist_contact:
                raise serializers.ValidationError(['Email {} already exists'.format(value)])
            return value


class VendorModuleNameSerializer(serializers.ModelSerializer):
    module = serializers.PrimaryKeyRelatedField(queryset=Modules.objects.all(), required=False, allow_null=True)

    class Meta:
        model = VendorModuleNames
        fields = ("module",)


class VendorsCsvSerializer(serializers.ModelSerializer):
    contacts = VendorContactSerializer(many=True)
    modules = VendorModuleNameSerializer(many=True, required=False)

    class Meta:
        model = Vendors
        fields = ('vendor_name',
                  'country',
                  'nda',
                  'contacts',
                  'modules',)

    def create(self, validated_data):
        contact_data = validated_data.pop('contacts', None)
        modules = validated_data.pop('modules', None)
        # Only for first phase for workin with admin instancess only. Rewrite after !!!
        superuser = CustomUser.objects.filter(is_superuser=True)
        if superuser:
            current_user = superuser[0]
            superuser_id = current_user.id
        else:
            raise ValueError('Create superuser first')
        vendor = Vendors.objects.create(**validated_data, user_id=superuser_id)
        for data in contact_data:
            try:
                VendorContacts.objects.create(vendor=vendor, **data)
            except DataError as e:
                raise serializers.ValidationError({"general_errors":
                                                  ["Some data are incorrect (possibly too long email value)"]})
        if modules:
            for data in modules:
                VendorModuleNames.objects.create(vendor=vendor, vendor_name=vendor.vendor_name,
                                                 user=current_user, **data)
        return vendor


class VendorContactManualSerializer(serializers.ModelSerializer):
    email = serializers.CharField(validators=[RegexValidator(regex=r'[^@]+@[^\.]+\..+',
                                                             message='Enter valid email address')], allow_blank=True)

    class Meta:
        model = VendorContacts
        fields = ('contact_id',
                  'contact_name',
                  'phone',
                  'email',
                  'primary',
                    )
        read_only_fields = ('contact_id', )


class VendorsCreateSerializer(serializers.ModelSerializer):
    contacts = VendorContactManualSerializer(many=True)
    parent = serializers.PrimaryKeyRelatedField(queryset=Vendors.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Vendors
        fields = ('vendor_name',
                  'country',
                  'nda',
                  'contacts',
                  'parent',)

    def validate(self, data):
        # Check that response contact is/not parent contact. If not parent contact - raise exception
        parent = data.get('parent', None)
        email_list = data.get('contacts', None)
        for e in email_list:
            email = e.get('email', None)  # get request email
        if parent:
            p_contact_email_list = []
            parent_contact = VendorContacts.objects.filter(vendor=parent)
            for contact in parent_contact:
                p_contact_email_list.append(contact.email)  # get list of parent vendors emails
            if email != "":
                if email in p_contact_email_list:
                    pass
                else:
                    exist_contact = VendorContacts.objects.filter(email=email).filter(vendor__active=True)
                    if exist_contact:
                        raise serializers.ValidationError({"contacts":
                                                               [{'email': ['Email {} already exists'.format(email)]}]})

        else:
            exist_contact = VendorContacts.objects.filter(email=email).filter(vendor__active=True)
            if exist_contact:
                raise serializers.ValidationError({"contacts":
                                                       [{'email': ['Email {} already exists'.format(email)]}]})
        return data

    def create(self, validated_data):
        contact_data = validated_data.pop('contacts')
        # Only for first phase for workin with admin instancess only. Rewrite after !!!
        superuser = CustomUser.objects.filter(is_superuser=True)
        if superuser:
            superuser_id = superuser[0].id
            vendor = Vendors.objects.create(**validated_data, user_id=superuser_id)
        else:
            raise ValueError('Create superuser first')
        for data in contact_data:
            VendorContacts.objects.create(vendor=vendor, primary=True, **data)
        return vendor


class VendorModulSerializer(serializers.ModelSerializer):

    class Meta:
        model = VendorModuleNames
        fields = ('module',)


class ModulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modules
        fields = ('mid', 'module_name', )


# RFI
class RfiParticipationCsvSerializer(serializers.ModelSerializer):

    class Meta:
        model = RfiParticipation
        fields = ('pk', 'active', 'm', 'rfi', 'vendor', 'timestamp')
        read_only_fields = ('timestamp', )

    def get_unique_together_validators(self):
        """Overriding method to disable unique together checks"""
        return []

    def create(self, validated_data):
        module, created = RfiParticipation.objects.update_or_create(
            rfi=validated_data.get('rfi', None),
            vendor=validated_data.get('vendor', None),
            m=validated_data.get('m', None),
            defaults={'active': validated_data.get('active', False)})
        return module


class RfiParticipationSerializer(serializers.ModelSerializer):
    rfi = serializers.PrimaryKeyRelatedField(queryset=Rfis.objects.all(), required=False, allow_null=True)

    class Meta:
        model = RfiParticipation
        fields = ('pk', 'active', 'm', 'rfi', 'vendor', 'timestamp')
        read_only_fields = ('timestamp', )

    def get_unique_together_validators(self):
        """Overriding method to disable unique together checks"""
        return []

    def create(self, validated_data):
        superuser = CustomUser.objects.filter(is_superuser=True)
        if superuser:
            superuser_id = superuser[0].id
        else:
            raise ValueError('Create superuser first')
        rfi = validated_data.get('rfi', None)
        # Allow send empty rfi data and apply last participate vendor round instead
        if not rfi:
            round = Rfis.objects.all()
            if round:
                lastr_round = round.order_by('-timestamp').first()
                validated_data['rfi'] = lastr_round
            else:
                raise serializers.ValidationError({"general_errors": ["Round is not created yet"]})

        module, created = RfiParticipation.objects.update_or_create(
            rfi=validated_data.get('rfi', None),
            vendor=validated_data.get('vendor', None),
            m=validated_data.get('m', None), user_id=superuser_id,
            defaults={'active': validated_data.get('active', False)})
        return module


class RfiParticipationCsvDownloadSerializer(serializers.ModelSerializer):

    class Meta:
        model = RfiParticipation
        fields = ('active', 'm',)

    def to_representation(self, instance):
        rep = super(RfiParticipationCsvDownloadSerializer, self).to_representation(instance)
        rep['m'] = instance.m.module_name
        return rep


class RfiRoundSerializer(serializers.ModelSerializer):
    creation_date = serializers.CharField(source='timestamp', required=False)

    class Meta:
        model = Rfis
        fields = (
             'rfi_status',
             'rfiid',
             'active',
             'issue_datetime',
             'open_datetime',
             'close_datetime',
             'creation_date'
            )
        read_only_fields = ('rfi_status', 'rfiid', 'timestamp')

    def create(self, validated_data):
        # Generate rfiid
        year_ = str(date.today().year)[:2]
        r = Rfis.objects.all().count()
        if r == 0:
            rfiid = year_ + 'R1'
        else:
            r = Rfis.objects.all().order_by('-timestamp').first()
            last_rfiid = r.rfiid
            round = (int(last_rfiid[-1]) + 1)
            rfiid = year_ + 'R' + str(round)
        # Check status
        current_time = datetime.datetime.today()
        rfi_status = 'Created'
        if validated_data['open_datetime'] < current_time < validated_data['issue_datetime']:
            rfi_status = "Opened"
        elif current_time >= validated_data['issue_datetime']:
            rfi_status = "Issued"
        round = Rfis.objects.create(rfiid=rfiid, rfi_status=rfi_status, **validated_data)

        return round

    def update(self, instance, validated_data):
        # Check status
        rfi_status = 'Created'
        current_time = datetime.datetime.today()
        if validated_data['open_datetime'] < current_time < validated_data['issue_datetime']:
            rfi_status = "Opened"
        elif current_time >= validated_data['issue_datetime']:
            rfi_status = "Issued"
        instance.rfi_status = rfi_status
        instance.save()
        return instance


class RfiRoundCloseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rfis
        fields = ('rfiid', 'active',)
        read_only_field = ('rfiid', 'active',)

    def update(self, instance, validated_data):
        instance.active = False
        instance.save()
        return instance


# RFI MANAGEMENT

class VendorModulesListManagementSerializer(serializers.ModelSerializer):
    # to_vendor = RfiParticipationSerializer(many=True)
    to_vendor = serializers.SerializerMethodField()

    class Meta:
        model = Vendors
        fields = ('vendorid', 'vendor_name', 'to_vendor',)
        read_only_fields = ('vendorid', 'vendor_name', )

    def get_to_vendor(self, obj):
        """
        Return only rfi for current round (get from url)
        :param obj:
        :return:
        """
        rfiid = self.context.get('rfiid')
        r = RfiParticipation.objects.filter(vendor=obj, rfi=rfiid)
        serializer = RfiParticipationSerializer(r, many=True)
        return serializer.data



# VENDOR PROFILE

class VendorsManagementListSerializer(serializers.ModelSerializer):
    company_information = serializers.SerializerMethodField()
    vendor_modules = serializers.SerializerMethodField()

    class Meta:
        model = Vendors
        fields = ('vendor_name',
                  'vendorid',
                  'active',
                  'company_information',
                  'vendor_modules',)

    def get_company_information(self, obj):
        # Calculate last edited rfi participation module and get round information
        rfi_id = None
        round = Rfis.objects.filter()
        if round:
            vendor_module_round = RfiParticipation.objects.filter(vendor=obj)
            if vendor_module_round:
                last_vendor_module_round = vendor_module_round.order_by('-timestamp').first()
                if last_vendor_module_round:
                    rfi_id = last_vendor_module_round.rfi.rfiid
                else:
                    rfi_id = None
        return rfi_id

    def get_vendor_modules(self, obj):
        # check round for all participate modules
        # Using F for rename field relationship name
        r = RfiParticipation.objects.filter(vendor=obj).order_by('rfi').\
                                     values(module=F('m__module_name'), round=F('rfi'))
        return r


class VendorManagementUpdateSerializer(serializers.ModelSerializer):
    contacts = VendorContactSerializer(many=True)
    parent = serializers.PrimaryKeyRelatedField(queryset=Vendors.objects.all(), required=False, allow_null=True)
    to_vendor = RfiParticipationSerializer(many=True)
    history = serializers.SerializerMethodField()
    current_round_participate = serializers.SerializerMethodField()
    office = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = Vendors
        fields = ('vendorid',
                  'vendor_name',
                  'active',
                  'country',
                  'office',
                  'abr_date',
                  'nda',
                  'parent',
                  'contacts',
                  'to_vendor',
                  'history',
                  'current_round_participate',
                  )
        read_only_fields = ('history', 'current_round_participate')

    def update(self, instance, validated_data):
        # raise_errors_on_nested_writes('update', self, validated_data)
        for attr, value in validated_data.items():
            if attr == 'nda':
                # TODO remove partisipate to round modules
                pass
            if attr == 'office':
                # TODO remove partisipate to round modules
                pass
            setattr(instance, attr, value)
        if validated_data.get("vendor_name", None):
            instance.save()
        else:
            instance.save_without_historical_record()
        return instance

    def validate_nda(self, value):
        if value is not None:
            curent_date = datetime.date.today()
            if value > curent_date:
                raise serializers.ValidationError(['Future date is not allowed'])
        return value

    def get_history(self, obj):
        h = obj.history.all().order_by('-history_date').values('vendor_name')[1:]
        return h

    def get_current_round_participate(self, obj):
        round_exist = Rfis.objects.filter()
        if round_exist:
            current_round = round_exist.order_by('-timestamp').first()
            vendor_module_round = RfiParticipation.objects.filter(vendor=obj, rfi=current_round)
            if vendor_module_round:
                _round = True
            else:
                _round = False
        else:
            _round = False
        return _round

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['parent'] = VendorToFrontSerializer(instance.parent).data
        return response


class VendorContactCreateSerializer(serializers.ModelSerializer):
    email = serializers.CharField(validators=[RegexValidator(regex=r'[^@]+@[^\.]+\..+',
                                                             message='Enter valid email address')])
    vendor = serializers.PrimaryKeyRelatedField(queryset=Vendors.objects.all(), required=False, allow_null=True)
    phone = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = VendorContacts
        fields = ('vendor',
                  'contact_name',
                  'contact_id',
                  'phone',
                  'email',
                  'primary',
                  )
        read_only_fields = ('contact_id', )

    def validate_email(self, value):
        if len(value) > 80:
            raise serializers.ValidationError(['Email is too long'])
        exist_contact = VendorContacts.objects.filter(email=value)
        vendors = Vendors.objects.filter(active=True)
        if exist_contact:
            for contact in exist_contact:
                if contact.vendor in vendors:
                    raise serializers.ValidationError(['Email {} already exists'.format(value)])
        return value


class ContactUpdateSerializer(serializers.ModelSerializer):
    vendor = serializers.PrimaryKeyRelatedField(queryset=Vendors.objects.all(), required=False, allow_null=True)

    class Meta:
        model = VendorContacts
        fields = ('contact_id',
                  'contact_name',
                  'phone',
                  'email',
                  'primary',
                  'vendor',
                    )
        read_only_fields = ('contact_id', 'vendor')

    def validate_email(self, value):
        if self.instance and value != self.instance.email:
            vendor = self.instance.vendor
            parent = vendor.parent
            # Check that response contact is/not parent contact. If not parent contact - raise exception
            if parent:
                p_contact_email_list = []
                parent_contact = VendorContacts.objects.filter(vendor=parent)
                for contact in parent_contact:
                    p_contact_email_list.append(contact.email)  # get list of parent vendors emails
                if value != "":
                    if value in p_contact_email_list:
                        pass
                    else:
                        exist_contact = VendorContacts.objects.filter(email=value).filter(vendor__active=True)
                        if exist_contact:
                            raise serializers.ValidationError(['Email {} already exists'.format(value)])
            else:
                exist_contact = VendorContacts.objects.filter(email=value).filter(vendor__active=True)
                if exist_contact:
                    raise serializers.ValidationError(['Email {} already exists'.format(value)])
        return value

    def update(self, instance, validated_data):
        # raise_errors_on_nested_writes('update', self, validated_data)
        for attr, value in validated_data.items():
            if attr == 'email':
                value = value.lower()
            setattr(instance, attr, value)
        instance.save()

        return instance


# EXCEL
class ParentcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentCategories
        fields = (
            'parent_category_name',
        )


class CategoriesSerializer(serializers.ModelSerializer):
    pc = serializers.PrimaryKeyRelatedField(queryset=ParentCategories.objects.all())
    class Meta:
        model = Categories
        fields = (
            'pc',
            'category_name',
        )


class SubcategoriesSerializer(serializers.ModelSerializer):
    c = serializers.PrimaryKeyRelatedField(queryset=Categories.objects.all())
    class Meta:
        model = Subcategories
        field = (
            'c',
            'subcategory_name',
            )


class ElementsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Elements
        field = (
            's',
            'element_name',
            'description',
            'scoring_scale',
            'e_order',
            )


class SelfDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelfDescriptions
        fields = (
            'vendor',
            'e',
            'self_description',
            'rfi',
            'vendor_response',
            )


class SelfScoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = SelfScores
        field = (
            'self_score',
        )


class AnalistNotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalystNotes
        field = (
            'vendor',
            'e',
            'analyst_notes',
            'rfi',
            'analyst_response',
            )


class SmScoresSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmScores
        field = (
            'vendor',
            'e',
            'sm_score',
            'rfi',
            'analyst_response',
            )


class ModuleElementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModuleElements
        field = (
            'm',
            'e',
            'rfi',
            )


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachments
        field = (
            'vendor',
            'filename',
            'extension',
            'path',
            'notes',
            'rfi',
            )


class ElementsAttachment(serializers.ModelSerializer):
    class Meta:
        model = ElementsAttachments
        field = (
            'e',
            'attachment',
            'rfi',
            'vendor_response',
            )


class CompanyInfoQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyGeneralInfoQuestion


class CompanyInfoAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyGeneralInfoAnswers


class ElementCommonInfoSerializer(serializers.ModelSerializer):

    s = serializers.CharField(required=False, allow_null=True)
    self_description = serializers.CharField(required=False, allow_null=True,
                                             validators=[RegexValidator(regex=r'^[a-zA-Z0-9,.!? -/*()]*$',
                                                                        message='The system detected that the data is not in English. '
                                                                                'Please correct the error and try again.')]
                                             )
    self_score = serializers.CharField(required=False, allow_null=True,
                                       validators=[RegexValidator(regex=r'^[0-5]',
                                                                  message='Self_score invalid value. Mast be between 0 and 5')]
                                       )
    sm_score = serializers.CharField(required=False, allow_null=True,
                                     validators=[RegexValidator(regex=r'^[0-5]',
                                                                message='Sm_score invalid value. Mast be between 0 and 5')]
                                     )
    analyst_notes = serializers.CharField(required=False, allow_null=True,
                                          validators=[RegexValidator(regex=r'^[a-zA-Z0-9,.!? -/*()]*$',
                                                                     message='The system detected that the data is not in English. '
                                                                             'Please correct the error and try again.')]
                                          )
    attachment = serializers.CharField(required=False, allow_null=True)
    category = serializers.CharField(required=False, allow_null=True)
    pc = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = Elements
        fields = ('element_name', 'description', 'scoring_scale', 'e_order', 'self_score',
                  'self_description', 'sm_score', 'analyst_notes', 'attachment', 's', 'category', 'pc')

    def create(self, validated_data):
        # Get data from url context
        rfiid = self.context.get('rfiid')
        vendor_id = self.context.get('vendor')
        analyst_id = self.context.get('analyst')
        vendor = Vendors.objects.get(vendorid=vendor_id)
        round = Rfis.objects.get(rfiid=rfiid)


        #TODO Get pc status from context for update
        # pc_status_info = self.context.get('pc_status_info')
        # last_s_r_info = pc_status_info[0]

        # for update rfipartisipatiostatus analyst/vendor response (1 or 0)
        status_info = self.context.get('status_info')

        # save CI
        company_information = self.context.get('Company_info')
        for ci in company_information:
            ciq, _ = CompanyGeneralInfoQuestion.objects.get_or_create(question=ci.get('question'), rfi=round)
            cia, _ = CompanyGeneralInfoAnswers.objects.update_or_create(vendor=vendor, question=ciq,
                                                                        defaults={'answer': ci.get('answer')})

        # Get data from validated data
        sc = validated_data.pop('s')
        cat = validated_data.pop('category')
        pc = validated_data.pop('pc')
        self_score = validated_data.pop('self_score')
        self_description = validated_data.pop('self_description')
        sm_score = validated_data.pop('sm_score')
        analyst_notes = validated_data.pop('analyst_notes')
        attachment = validated_data.pop('attachment')

        parent_category = ParentCategories.objects.filter(parent_category_name=pc)
        if parent_category:
            category, _ = Categories.objects.get_or_create(category_name=cat, pc=parent_category.first())
        else:
            raise serializers.ValidationError({"general_errors": ["Parent categories are not exist"]})
        subcategory, _ = Subcategories.objects.get_or_create(subcategory_name=sc, c=category)

        if status_info:
            lar = status_info.get(pc, {}).get('analyst')
            lvr = status_info.get(pc, {}).get('vendor')
            rfi_part_status, _ = RfiParticipationStatus.objects.update_or_create(vendor=vendor, rfi=round,
                                                                                 pc=parent_category.first(),
                                                                                 defaults={'last_analyst_response': lar,
                                                                                           'last_vendor_response': lvr}
                                                                                 )

        element, _ = Elements.objects.get_or_create(**validated_data, s=subcategory)

        if analyst_id:
            analyst_notes, _ = AnalystNotes.objects.get_or_create(vendor=vendor, e=element, analyst_notes=analyst_notes,
                                                                  rfi=round, analyst_response=lar)

            sm_scores, _ = SmScores.objects.get_or_create(vendor=vendor, e=element, sm_score=sm_score, rfi=round,
                                                          analyst_response=lar)

        else:
            self_score, _ = SelfScores.objects.get_or_create(vendor=vendor, e=element, self_score=self_score, rfi=round,
                                                             vendor_response=lvr)

            self_description, _ = SelfDescriptions.objects.get_or_create(vendor=vendor, e=element,
                                                                         self_description=self_description, rfi=round,
                                                                         vendor_response=lvr)

            attachment, _ = Attachments.objects.get_or_create(vendor=vendor, path=attachment, rfi=round)

            element_attachment, _ = ElementsAttachments.objects.get_or_create(e=element, attachment=attachment,
                                                                              rfi=round, vendor_response=lvr)

        # module_element, _ = ModuleElements.objects.get_or_create(e=element, rfi=round, )

        return self


class CommonExcelUploadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rfis
        field = ("rfiid", )
import re
from datetime import date
import datetime

from django.db.models import F
from django.db import DataError
from django.core.validators import RegexValidator
from django.db.models import Max

from rest_framework import serializers

from apps.c_users.models import CustomUser
from .models import Vendors, VendorContacts, VendorModuleNames, Modules, Rfis, RfiParticipation, \
    Elements, Subcategories, Categories, ParentCategories, SelfDescriptions, SelfScores, \
    AnalystNotes, SmScores, ModuleElements, Attachments, ElementsAttachments, RfiParticipationStatus , \
    CompanyGeneralInfoQuestion, CompanyGeneralInfoAnswers, AssignedVendorsAnalysts

from drf_yasg.utils import swagger_serializer_method


class AnalystSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignedVendorsAnalysts
        fields = ('pk', 'name')


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
        if validated_data['active']:
            module, created = RfiParticipation.objects.update_or_create(
                rfi=validated_data.get('rfi', None),
                vendor=validated_data.get('vendor', None),
                m=validated_data.get('m', None),
                defaults={'active': validated_data.get('active', True)})
            if created:
                pcm = ParentCategories.objects.filter(parent_categories=validated_data.get('m', None))
                for p_c in pcm:
                    pc_to_module, _ = RfiParticipationStatus.objects.get_or_create(
                        rfi=validated_data.get('rfi', None),
                        vendor=validated_data.get('vendor', None),
                        pc=p_c
                    )
        if not validated_data['active']:
            RfiParticipation.objects.filter(rfi=validated_data.get('rfi'),
                                            vendor=validated_data.get('vendor'),
                                            m=validated_data.get('m'),).update(active=False)

        return self


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

        # create Rfipartstatus objects
        if created:
            pcm = ParentCategories.objects.filter(parent_categories=validated_data.get('m', None))
            for p_c in pcm:
                pc_to_module, _ = RfiParticipationStatus.objects.get_or_create(
                    rfi=validated_data.get('rfi', None),
                    vendor=validated_data.get('vendor', None),
                    pc=p_c
                )

        return module


class AssociateModulesToVendorsSerializer(serializers.ModelSerializer):
    m = serializers.PrimaryKeyRelatedField(queryset=Modules.objects.all(), required=False, allow_null=True)
    vendor = serializers.PrimaryKeyRelatedField(queryset=Vendors.objects.all(), required=False, allow_null=True)
    class Meta:
        model = RfiParticipation
        fields = ('active', 'm', 'vendor')

    def get_unique_together_validators(self):
        """Overriding method to disable unique together checks"""
        return []

    def create(self, validated_data):
        round_ = Rfis.objects.get(rfiid = self.context['rfiid'])
        module, created = RfiParticipation.objects.update_or_create(
            rfi=round_,
            vendor=validated_data.get('vendor', None),
            m=validated_data.get('m', None),
            defaults={'active': validated_data.get('active', False)})

        # create Rfipartstatus objects
        if created:
            pcm = ParentCategories.objects.filter(parent_categories=validated_data.get('m', None))
            for p_c in pcm:
                pc_to_module, _ = RfiParticipationStatus.objects.get_or_create(
                    rfi=round_,
                    vendor=validated_data.get('vendor', None),
                    pc=p_c
                )

        return self


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
        # Check that Status of all modules in the round are in Scored or Declined
        all_rfi_participate = RfiParticipationStatus.objects.filter(rfi=instance)
        to_popup = []
        for rfi_s in all_rfi_participate:
            if rfi_s.status not in ['Scored', 'Declined']:
                to_popup.append(f'{rfi_s.vendor} {rfi_s.pc.parent_category_name} is {rfi_s.status}')
        if len(to_popup):
            raise serializers.ValidationError({"general_errors": to_popup})

        else:
            for rfi_s in all_rfi_participate:
                rfi_s.status = "Closed"
                rfi_s.save()
            instance.active = False
            instance.status = 'Closed'
            instance.save()
        return instance


# RFI MANAGEMENT

class VendorModulesListManagementSerializer(serializers.ModelSerializer):
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
        cia = CompanyGeneralInfoAnswers.objects.filter(vendor=obj).order_by('-timestamp')
        if cia:
            last_ci = cia.first().question.rfi.rfiid
            rfi_id = last_ci
        else:
            rfi_id = None
        return rfi_id

    def get_vendor_modules(self, obj):
        vendor_modules = []
        modules = Modules.objects.all()
        for m in modules:
            if RfiParticipation.objects.filter(vendor=obj, m=m):
                last_round = RfiParticipation.objects.filter(vendor=obj, m=m).order_by('-timestamp').first()
                vendor_modules.append({'module': m.module_name, 'round': last_round.rfi.rfiid})

            else:
                vendor_modules.append({'module': m.module_name, 'round': None})
        return vendor_modules


class VendorManagementUpdateSerializer(serializers.ModelSerializer):
    contacts = VendorContactSerializer(many=True)
    parent = serializers.PrimaryKeyRelatedField(queryset=Vendors.objects.all(), required=False, allow_null=True)
    to_vendor = serializers.SerializerMethodField()
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

    # def get_to_vendor(self, obj):
    #     vendor_modules = []
    #     modules = Modules.objects.all()
    #     for m in modules:
    #         if RfiParticipation.objects.filter(vendor=obj, m=m):
    #             last_round = RfiParticipation.objects.filter(vendor=obj, m=m).order_by('-timestamp').first()
    #             vendor_modules.append({'pk': last_round.pk, 'active': last_round.active, 'rfi': last_round.rfi.rfiid,
    #                                    'm': m.pk, 'vendor': obj.pk,
    #                                    'timestamp': last_round.timestamp})
    #     return vendor_modules

    def get_to_vendor(self, obj):
        rp = RfiParticipation.objects.filter(vendor=obj).values('pk', 'active', 'rfi', 'm', 'vendor', 'timestamp')
        return rp

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

class CompanyInfoQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyGeneralInfoQuestion


class CompanyInfoAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyGeneralInfoAnswers


class ElementCommonInfoSerializer(serializers.ModelSerializer):

    s = serializers.CharField(required=False, allow_null=True)
    self_description = serializers.CharField(required=False, allow_null=True)
    self_score = serializers.CharField(required=False, allow_null=True)
    sm_score = serializers.CharField(required=False, allow_null=True)
    analyst_notes = serializers.CharField(required=False, allow_null=True)
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
        current_scoring_round = self.context.get('current_scoring_round')

        #TODO Get pc status from context for update
        # pc_status_info = self.context.get('pc_status_info')
        # last_s_r_info = pc_status_info[0]

        # for update rfipartisipatiostatus analyst/vendor response (1 or 0)
        status_info = self.context.get('status_info')

        # Get data from validated data
        sc = validated_data.pop('s')
        cat = validated_data.pop('category')
        pc = validated_data.pop('pc')
        self_score = validated_data.pop('self_score')
        self_description = validated_data.pop('self_description')
        sm_score = validated_data.pop('sm_score')
        analyst_notes = validated_data.pop('analyst_notes')
        attachment = validated_data.pop('attachment')
        e_order = validated_data.pop('e_order')
        parent_category = ParentCategories.objects.filter(parent_category_name=pc)
        if parent_category:
            category = Categories.objects.get(category_name=cat, pc=parent_category.first())
        else:
            raise serializers.ValidationError({"general_errors": ["Parent categories are not exist"]})
        subcategory = Subcategories.objects.get(subcategory_name=sc, c=category)

        # Deprecated, status changes depending on the scoring number of the round and not on the filling of the file.
        # if status_info:
        #     lar = status_info.get(pc, {}).get('analyst')
        #     lvr = status_info.get(pc, {}).get('vendor')
        #     rfi_part_status, _ = RfiParticipationStatus.objects.update_or_create(vendor=vendor, rfi=round,
        #                                                                          pc=parent_category.first(),
        #                                                                          defaults={'last_analyst_response': lar,
        #                                                                                    'last_vendor_response': lvr}
        #                                                                          )
        #
        # rfi_part_status, _ = RfiParticipationStatus.objects.update_or_create(vendor=vendor, rfi=round,
        #                                                                      pc=parent_category.first(),
        #                                                                      defaults={'last_analyst_response': current_scoring_round,
        #                                                                                'last_vendor_response': current_scoring_round}
        #                                                                      )

        element = Elements.objects.get(s=subcategory, e_order=e_order)

        if analyst_id:
            analyst_notes, _ = AnalystNotes.objects.get_or_create(vendor=vendor, e=element, analyst_notes=analyst_notes,
                                                                  rfi=round, analyst_response=current_scoring_round)

            sm_scores, _ = SmScores.objects.get_or_create(vendor=vendor, e=element, sm_score=sm_score, rfi=round,
                                                          analyst_response=current_scoring_round)

            rfi_part_status, _ = RfiParticipationStatus.objects.update_or_create(vendor=vendor, rfi=round,
                                                                                 pc=parent_category.first(),
                                                                                 defaults={
                                                                                     'last_analyst_response': current_scoring_round,
                                                                                     'status': 'Scored'}
                                                                                 )

        else:
            self_score, _ = SelfScores.objects.get_or_create(vendor=vendor, e=element, self_score=self_score, rfi=round,
                                                             vendor_response=current_scoring_round)

            self_description, _ = SelfDescriptions.objects.get_or_create(vendor=vendor, e=element,
                                                                         self_description=self_description, rfi=round,
                                                                         vendor_response=current_scoring_round)

            # attachment= Attachments.objects.create(vendor=vendor, path=attachment, rfi=round)

            element_attachment, _ = ElementsAttachments.objects.get_or_create(e=element, attachment_info=attachment,
                                                                              rfi=round, vendor=vendor,
                                                                              vendor_response=current_scoring_round)

            rfi_part_status, _ = RfiParticipationStatus.objects.update_or_create(vendor=vendor, rfi=round,
                                                                                 pc=parent_category.first(),
                                                                                 defaults={
                                                                                     'last_vendor_response': current_scoring_round,
                                                                                     'status': 'Received'}
                                                                                 )

        # # module_element, _ = ModuleElements.objects.get_or_create(e=element, rfi=round, )

        return self


    # def create(self, validated_data):
    #     # Get data from url context
    #     rfiid = self.context.get('rfiid')
    #     vendor_id = self.context.get('vendor')
    #     analyst_id = self.context.get('analyst')
    #     vendor = Vendors.objects.get(vendorid=vendor_id)
    #     round = Rfis.objects.get(rfiid=rfiid)
    #     current_scoring_round = self.context.get('current_scoring_round')
    #
    #     #TODO Get pc status from context for update
    #     # pc_status_info = self.context.get('pc_status_info')
    #     # last_s_r_info = pc_status_info[0]
    #
    #     # for update rfipartisipatiostatus analyst/vendor response (1 or 0)
    #     status_info = self.context.get('status_info')
    #
    #     # Get data from validated data
    #     sc = validated_data.pop('s')
    #     cat = validated_data.pop('category')
    #     pc = validated_data.pop('pc')
    #     self_score = validated_data.pop('self_score')
    #     self_description = validated_data.pop('self_description')
    #     sm_score = validated_data.pop('sm_score')
    #     analyst_notes = validated_data.pop('analyst_notes')
    #     attachment = validated_data.pop('attachment')
    #     parent_category = ParentCategories.objects.filter(parent_category_name=pc)
    #     if parent_category:
    #         category, _ = Categories.objects.get_or_create(category_name=cat, pc=parent_category.first())
    #     else:
    #         raise serializers.ValidationError({"general_errors": ["Parent categories are not exist"]})
    #     subcategory, _ = Subcategories.objects.get_or_create(subcategory_name=sc, c=category)
    #
    #     # Deprecated, status changes depending on the scoring number of the round and not on the filling of the file.
    #     # if status_info:
    #     #     lar = status_info.get(pc, {}).get('analyst')
    #     #     lvr = status_info.get(pc, {}).get('vendor')
    #     #     rfi_part_status, _ = RfiParticipationStatus.objects.update_or_create(vendor=vendor, rfi=round,
    #     #                                                                          pc=parent_category.first(),
    #     #                                                                          defaults={'last_analyst_response': lar,
    #     #                                                                                    'last_vendor_response': lvr}
    #     #                                                                          )
    #
    #     rfi_part_status, _ = RfiParticipationStatus.objects.update_or_create(vendor=vendor, rfi=round,
    #                                                                          pc=parent_category.first(),
    #                                                                          defaults={'last_analyst_response': current_scoring_round,
    #                                                                                    'last_vendor_response': current_scoring_round}
    #                                                                          )
    #
    #     element, _ = Elements.objects.get_or_create(**validated_data, s=subcategory, initialize=False)
    #     if _:
    #         print('element create')
    #
    #     if analyst_id:
    #         analyst_notes, _ = AnalystNotes.objects.get_or_create(vendor=vendor, e=element, analyst_notes=analyst_notes,
    #                                                               rfi=round, analyst_response=current_scoring_round)
    #
    #         sm_scores, _ = SmScores.objects.get_or_create(vendor=vendor, e=element, sm_score=sm_score, rfi=round,
    #                                                       analyst_response=current_scoring_round)
    #
    #         rfi_part_status, _ = RfiParticipationStatus.objects.update_or_create(vendor=vendor, rfi=round,
    #                                                                              pc=parent_category.first(),
    #                                                                              defaults={
    #                                                                                  'last_analyst_response': current_scoring_round}
    #                                                                              )
    #
    #     else:
    #         self_score, _ = SelfScores.objects.get_or_create(vendor=vendor, e=element, self_score=self_score, rfi=round,
    #                                                          vendor_response=current_scoring_round)
    #
    #         self_description, _ = SelfDescriptions.objects.get_or_create(vendor=vendor, e=element,
    #                                                                      self_description=self_description, rfi=round,
    #                                                                      vendor_response=current_scoring_round)
    #
    #         # attachment= Attachments.objects.create(vendor=vendor, path=attachment, rfi=round)
    #
    #         element_attachment, _ = ElementsAttachments.objects.get_or_create(e=element, attachment_info=attachment,
    #                                                                           rfi=round, vendor=vendor,
    #                                                                           vendor_response=current_scoring_round)
    #
    #         rfi_part_status, _ = RfiParticipationStatus.objects.update_or_create(vendor=vendor, rfi=round,
    #                                                                              pc=parent_category.first(),
    #                                                                              defaults={
    #                                                                                  'last_vendor_response': current_scoring_round}
    #                                                                              )
    #
    #     # # module_element, _ = ModuleElements.objects.get_or_create(e=element, rfi=round, )
    #
    #     return self


class DownloadExcelSerializer(serializers.ModelSerializer):
    scoring_status = serializers.SerializerMethodField()
    class Meta:
        model = Vendors
        fields = ('vendorid', 'vendor_name', 'scoring_status',)

    def get_scoring_status(self, obj):
        rfiid = self.context.get('rfiid')

        # Check active module participate to vendor at round
        if not RfiParticipation.objects.filter(vendor=obj, rfi=rfiid, active=True):
            return None
        r = 1

        # Check that vendor have roundstatus object in round
        if RfiParticipationStatus.objects.filter(vendor=obj, rfi=rfiid):
            max_score = RfiParticipationStatus.objects.filter(vendor=obj, rfi=rfiid).aggregate(Max('last_vendor_response'),
                                                                                               Max('last_analyst_response'))
            # if max_score.get('last_vendor_response__max') != 0 and max_score.get('last_analyst_response__max') != 0:
            #     r = (max_score.get('last_analyst_response__max')) + 1
            # elif max_score.get('last_vendor_response__max') != 0 or max_score.get('last_analyst_response__max') != 0:
            #     r = max(max_score.get('last_vendor_response__max'), max_score.get('last_analyst_response__max'))
            # elif max_score.get('last_vendor_response__max') == 0 or max_score.get('last_analyst_response__max') == 0:
            #     r = 1
            if max_score.get('last_vendor_response__max') == max_score.get('last_analyst_response__max'):
                r = (max_score.get('last_analyst_response__max')) + 1
            else:
                r = (max_score.get('last_vendor_response__max'))
        return r


# Initialization of the zero template creation (only description of elements) for the first vendor upload

class ElementInitializeInfoSerializer(serializers.ModelSerializer):

    s = serializers.CharField(required=False, allow_null=True)
    category = serializers.CharField(required=False, allow_null=True)
    pc = serializers.CharField(required=False, allow_null=True)

    class Meta:
        model = Elements
        fields = ('element_name', 'description', 'scoring_scale', 'e_order', 's', 'category', 'pc')

    def create(self, validated_data):

        # Get data from validated data
        sc = validated_data.pop('s')
        cat = validated_data.pop('category')
        pc = validated_data.pop('pc')
        parent_category = ParentCategories.objects.filter(parent_category_name=pc)
        if parent_category:
            # parent_category.first().status = "Outstanding"
            category, _ = Categories.objects.get_or_create(category_name=cat, pc=parent_category.first())
        else:
            raise serializers.ValidationError({"general_errors": ["Parent categories are not exist"]})
        subcategory, _ = Subcategories.objects.get_or_create(subcategory_name=sc, c=category)

        element, _ = Elements.objects.get_or_create(**validated_data, s=subcategory)

        return self


# Vendor activity report

class VendorActivityReportUpdateSerializer(serializers.Serializer):
    module_id = serializers.SerializerMethodField()

    class Meta:
        model = RfiParticipation
        fields = ('module_id',)

    def update(self, instance, validated_data):
        # instance - global module
        rfi = self.context.get('rfi')
        vendor = self.context.get('vendor')
        pc_to_module = ParentCategories.objects.filter(parent_categories=instance).values('parent_category_name')
        pc_name_list = [",".join(list(d.values())) for d in pc_to_module]
        for pcn in pc_name_list:
            pc_st = RfiParticipationStatus.objects.get(vendor=vendor, rfi=rfi, pc__parent_category_name=pcn)
            pc_st.status = "Declined"
            pc_st.save()
        # Change module-to-rfi status active to False
        rfi_part = RfiParticipation.objects.get(vendor=vendor, rfi=rfi, m=instance)
        rfi_part.active = False
        rfi_part.save()
        return instance


class VendorActivityReportSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    module_id = serializers.SerializerMethodField()

    class Meta:
        model = RfiParticipation
        fields = ('module_id', 'm', 'status')

    def to_representation(self, instance):
        rep = super(VendorActivityReportSerializer, self).to_representation(instance)
        rep['m'] = instance.m.module_name
        return rep

    def get_module_id(self, obj):
        return obj.m.pk

    def get_status(self, obj):
        status_list = ["Invited", "Declined", "Accepted", "Created", "Outstanding", "Received", "Scored", "Closed"]
        round = self.context.get('round')
        vendor = self.context.get('vendor')
        pc_to_module = ParentCategories.objects.filter(parent_categories__module_name=obj.m.module_name)
        if not pc_to_module:
            raise serializers.ValidationError({"general_errors": ["Parent categories are not exist"]})
        min_status = "Closed"
        for pc in pc_to_module:
            pc_status = RfiParticipationStatus.objects.get(rfi=round, vendor=vendor, pc=pc)
            c_status = pc_status.status
            if status_list.index(c_status) < status_list.index(min_status):
                min_status = c_status
        to_calculate_round = []
        if min_status not in ["Invited", "Declined", "Accepted", "Created", "Outstanding",]:
            m_status = "Closed"
            for pc in pc_to_module:
                pc_status = RfiParticipationStatus.objects.get(rfi=round, vendor=vendor, pc=pc)
                if pc_status.status in ["Received", "Scored", "Closed"]:
                    to_calculate_round.append([pc_status.status, pc_status.last_vendor_response, pc_status.last_analyst_response])
                for _ in to_calculate_round:
                    c_status = _[0]
                    if status_list.index(c_status) < status_list.index(m_status):
                        m_status = c_status

            if min_status == "Closed":
                minimum = 100
                sum_round = [[i[0], sum(i[1:3])] for i in to_calculate_round]
                for i in sum_round:
                    if i[1] < minimum:
                        minimum = i[1]
                return f'Closed{int(minimum/2)}'
            else:
                to_calculate_round = [i for i in to_calculate_round if i[0] != "Closed"]
                sum_round = [[i[0], sum(i[1:3])] for i in to_calculate_round]
                final_compare_status = {"Received": 100, "Scored": 100}
                for _ in sum_round:
                    if _[0] == "Received":
                        if _[1] < final_compare_status.get('Received'):
                            final_compare_status['Received'] = _[1]
                    if _[0] == 'Scored':
                        if _[1] < final_compare_status.get('Scored'):
                            final_compare_status['Scored'] = _[1]
                if final_compare_status.get("Scored") == final_compare_status.get('Received'):
                    score = int(final_compare_status.get('Received')/2)
                    if score == 0:
                        score = 1
                    min_status = f'Received{score}'
                    return min_status
                else:
                    min_status = min(final_compare_status, key=final_compare_status.get)
                    score = int(final_compare_status.get(min_status)/2)
                    if score == 0:
                        score = 1
                    min_status = f'{min_status}{score}'
        return min_status


class DashboardVendorsModuleSerializer(serializers.Serializer):
    name = serializers.CharField()
    rfi = serializers.CharField()


class DashboardVendorsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='vendorid')
    modules = serializers.SerializerMethodField()
    last_company_info_update = serializers.SerializerMethodField()

    LAST_RFI_FOR_MODULES_SQL = """
    SELECT  rfi_participation.id, rfi_participation.vendor_id, rfi_participation.rfi_id, modules.module_name
    FROM rfi_participation
    INNER JOIN modules ON rfi_participation.m_id = modules.mid AND modules.active = TRUE
    LEFT JOIN  rfi_participation as rfi_p
    ON rfi_participation.m_id = rfi_p.m_id AND
       rfi_participation.timestamp < rfi_p.timestamp AND rfi_participation.vendor_id = rfi_p.vendor_id
    WHERE rfi_p.id IS NULL AND rfi_participation.active = TRUE
    """

    rfi_participation = RfiParticipation.objects.raw(LAST_RFI_FOR_MODULES_SQL)

    class Meta:
        model = Vendors
        fields = ('id',
                  'vendor_name',
                  'active',
                  'modules',
                  'last_company_info_update',
                  )

    @swagger_serializer_method(DashboardVendorsModuleSerializer(many=True))
    def get_modules(self, obj):
        modules = []

        for rfi_p in self.rfi_participation:
            if rfi_p.vendor_id == obj.vendorid:
                modules.append({'name': rfi_p.module_name, 'rfi': rfi_p.rfi_id})

        return modules

    def get_last_company_info_update(self, obj):
        info = CompanyGeneralInfoAnswers.objects.filter(vendor_id=obj.vendorid).order_by('-timestamp').first()

        if info:
            return info.question.rfi_id
        else:
            return None

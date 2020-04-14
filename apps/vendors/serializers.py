import re
from datetime import date
import datetime

from django.db.models import F
from django.db import DataError
from django.shortcuts import get_object_or_404
from django.core.validators import RegexValidator

from rest_framework import serializers

from apps.c_users.models import CustomUser
from .models import Vendors, VendorContacts, VendorModuleNames, Modules, Rfis, RfiParticipation, RfiParticipationStatus


class VendorToFrontSerializer(serializers.ModelSerializer):
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

    # def update(self, instance, validated_data):
    #     phone = validated_data.pop('phone', instance.phone)
    #     result = re.sub('[^0-9]','', phone)
    #     instance.phone = result
    #     instance.email = validated_data.get('email', instance.email)
    #     instance.contact_name = validated_data.get('contact_name', instance.contact_name)
    #     instance.save()
    #     return instance

    def validate_email(self, value):
        # Check if email exist in active vendor and raise exception
        exist_contact = VendorContacts.objects.filter(email=value)
        vendors = Vendors.objects.filter(active=True)
        if exist_contact:
            for contact in exist_contact:
                if contact.vendor in vendors:
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

    # def update(self, instance, validated_data):
    #     phone = validated_data.pop('phone', instance.phone)
    #     result = re.sub('[^0-9]','', phone)
    #     instance.phone = result
    #     instance.email = validated_data.get('email', instance.email)
    #     instance.contact_name = validated_data.get('contact_name', instance.contact_name)
    #     instance.save()
    #     return instance


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
        fields = ('active',)

    def update(self, instance, validated_data):
        # raise_errors_on_nested_writes('update', self, validated_data)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


# RFI MANAGEMENT

class VendorModulesListManagementSerializer(serializers.ModelSerializer):
    to_vendor = RfiParticipationSerializer(many=True)

    class Meta:
        model = Vendors
        fields = ('vendorid', 'vendor_name', 'to_vendor',)
        read_only_fields = ('vendorid', 'vendor_name', )


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
            setattr(instance, attr, value)
        if attr == 'vendor_name':
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

    # def create(self, validated_data):
    #     phone = validated_data.pop('phone', None)
    #     vendor = validated_data.pop('vendor', None)
    #     result = re.sub('[^0-9]', '', phone)
    #     contact = VendorContacts.objects.create(vendor=vendor, phone=result, **validated_data)
    #     return contact

    def validate_email(self, value):
        exist_contact = VendorContacts.objects.filter(email=value)
        vendors = Vendors.objects.filter(active=True)
        if exist_contact:
            for contact in exist_contact:
                if contact.vendor in vendors:
                    raise serializers.ValidationError(['Email {} already exists'.format(value)])
        return value


class ContactUpdateSerializer(serializers.ModelSerializer):
    vendor = serializers.PrimaryKeyRelatedField(queryset=Vendors.objects.all())

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
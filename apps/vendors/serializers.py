import re
from datetime import date
import datetime
from django.db.models import F

from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from rest_framework.response import Response
from rest_framework import status

from apps.c_users.models import CustomUser
from .models import Vendors, VendorContacts, VendorModuleNames, Modules, Rfis, RfiParticipation, RfiParticipationStatus


class VendorToFrontSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendors
        fields = ('pk', 'vendor_name')


class VendorContactSerializer(serializers.ModelSerializer):
    email = serializers.CharField(validators=[RegexValidator(regex=r'[^@]+@[^\.]+\..+',
                                                             message='Enter valid email address')])

    class Meta:
        model = VendorContacts
        fields = ('contact_id',
                  'contact_name',
                  'phone',
                  'email',
                  'primary',
                    )
        read_only_fields = ('contact_id', )

    def update(self, instance, validated_data):
        phone = validated_data.pop('phone', instance.phone)
        result = re.sub('[^0-9]','', phone)
        instance.phone = result
        instance.email = validated_data.get('email', instance.email)
        instance.contact_name = validated_data.get('contact_name', instance.contact_name)
        instance.save()
        return instance


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
            VendorContacts.objects.create(vendor=vendor, **data)
        if modules:
            for data in modules:
                VendorModuleNames.objects.create(vendor=vendor, vendor_name=vendor.vendor_name,
                                                 user=current_user, **data)

        # Filter: only if we decide using modules from VendorModuleName list
        # if modules:
        #     for data in modules:
        #         vmn = VendorModuleNames.objects.create(vendor=vendor, vendor_name=vendor.vendor_name,
        #                                          user=current_user, **data)
        #         modules = Modules.objects.get(module_name=vmn.module.module_name)
        #         RfiParticipation.objects.create(vendor=vendor, user_id=superuser_id,  m=modules)

        # Extra: create RfiParticipation tables with default active status = False
        return vendor


class VendorsCreateSerializer(serializers.ModelSerializer):
    contacts = VendorContactSerializer(many=True)
    parent = serializers.PrimaryKeyRelatedField(queryset=Vendors.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Vendors
        fields = ('vendor_name',
                  'country',
                  'nda',
                  'contacts',
                  'parent',)

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

class RfiParticipationSerializer(serializers.ModelSerializer):

    class Meta:
        model = RfiParticipation
        fields = ('pk', 'active', 'm', 'rfi', 'vendor', 'timestamp')
        read_only_fields = ('timestamp', )

    def create(self, validated_data):
        superuser = CustomUser.objects.filter(is_superuser=True)
        if superuser:
            superuser_id = superuser[0].id
        else:
            raise ValueError('Create superuser first')
        module, created = RfiParticipation.objects.update_or_create(
            rfi=validated_data.get('rfi', None),
            vendor=validated_data.get('vendor', None),
            m=validated_data.get('m', None), user_id=superuser_id,
            defaults={'active': validated_data.get('active', False)})
        return module

    def to_representation(self, instance):
        rep = super(RfiParticipationSerializer, self).to_representation(instance)
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
        last_round = RfiParticipation.objects.filter(vendor=obj).order_by('-timestamp').first()
        return last_round.rfi.rfiid

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
                  )


class VendorContactCreateSerializer(serializers.ModelSerializer):
    email = serializers.CharField(validators=[RegexValidator(regex=r'[^@]+@[^\.]+\..+',
                                                             message='Enter valid email address')])
    vendor = serializers.PrimaryKeyRelatedField(queryset=Vendors.objects.all(), required=False, allow_null=True)

    class Meta:
        model = VendorContacts
        fields = ('vendor',
                  'contact_name',
                  'phone',
                  'email',
                  'primary',
                  )

    def create(self, validated_data):
        phone = validated_data.pop('phone', None)
        vendor = validated_data.pop('vendor', None)
        result = re.sub('[^0-9]', '', phone)
        contact = VendorContacts.objects.create(vendor=vendor, phone=result, **validated_data)
        return contact

    def validate_email(self, value):
        if VendorContacts.objects.filter(email=value):
            raise serializers.ValidationError('Email {} already exists'.format(value))
        return value

from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from rest_framework.response import Response
from rest_framework import status

from apps.c_users.models import CustomUser
from .models import Vendors, VendorContacts, VendorModuleNames, Modules


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
            vendor = Vendors.objects.create(**validated_data, user_id=superuser_id)
        else:
            raise ValueError('Create superuser first')
        for data in contact_data:
            VendorContacts.objects.create(vendor=vendor, **data)
        if modules:
            for data in modules:
                VendorModuleNames.objects.create(vendor=vendor, vendor_name=vendor.vendor_name,
                                                 user=current_user, **data)
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
    serializers.RelatedField(source='module.id', read_only='True', many=True)

    class Meta:
        model = VendorModuleNames
        fields = ('module',)


class ModulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modules
        fields = ('mid', 'module_name', )


class VendorManagementListSerializer(serializers.ModelSerializer):
    vendor_modules = VendorModulSerializer(many=True)

    class Meta:
        model = Vendors
        fields = ('vendor_name',
                  'vendorid',
                  'active',
                  'vendor_modules',)


class VendorManagementUpdateSerializer(serializers.ModelSerializer):
    contacts = VendorContactSerializer(many=True)
    parent = serializers.PrimaryKeyRelatedField(queryset=Vendors.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Vendors
        fields = ('vendorid',
                  'vendor_name',
                  'active',
                  'country',
                  'nda',
                  'parent',
                  'contacts',
                  )

    # def update(self, instance, validated_data):
    #     instance = validated_data.get('vendor_name', instance.vendor_name)
    #     instance.save()
    #     return instance
    def update(self, instance, validated_data):
        # raise_errors_on_nested_writes('update', self, validated_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance

# class VendorManagementContactUpdateDeleteSerializer(serializers.ModelSerializer):
#     # contacts = VendorContactSerializer(many=True)
#     parent = serializers.PrimaryKeyRelatedField(queryset=Vendors.objects.all(), required=False, allow_null=True)
#
#     class Meta:
#         model = Vendors
#         fields = ('vendorid',
#                   'vendor_name',
#                   'active',
#                   'country',
#                   'nda',
#                   'parent',
#                   )
#
#     # def update(self, instance, validated_data):
#     #     instance = validated_data.get('vendor_name', instance.vendor_name)
#     #     instance.save()
#     #     return instance
#     def update(self, instance, validated_data):
#         # raise_errors_on_nested_writes('update', self, validated_data)
#
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#         instance.save()
#
#         return instance


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

    def validate_email(self, value):
        if VendorContacts.objects.filter(email=value):
            raise serializers.ValidationError('Email {} already exists'.format(value))
        return value

from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist

from apps.c_users.models import CustomUser
from .models import Vendors, VendorContacts, VendorModuleNames, Modules


class VendorToFrontSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendors
        fields = ('pk', 'vendor_name')


class VendorContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorContacts
        fields = (
                  'contact_name',
                  'phone',
                  'email',)

    # def validate_email(self, value):
    #     if get_object_or_404(VendorContacts, email=value) and value != "":
    #         raise serializers.ValidationError("email must be unique")
    #     else:
    #         print("False")
    #
    # def create(self, validated_data):
    #     email = validated_data.pop('email')
    #     # if VendorContacts.objects.get(email = email):
    #     #     raise
    #     return self


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

        for data in contact_data:
            VendorContacts.objects.create(vendor=vendor, **data)
        if modules:
            for data in modules:
                VendorModuleNames.objects.create(vendor=vendor, vendor_name=vendor.vendor_name, user=current_user, **data)
        return vendor


class VendorsSerializer(serializers.ModelSerializer):
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
            vendor = Vendors.objects.create(**validated_data)
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
        fields = ('module_name', )

from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist

from apps.c_users.models import CustomUser
from .models import Vendors, VendorContacts, VendorModuleNames, Modules


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


class VendorsSerializer(serializers.ModelSerializer):
    contacts = VendorContactSerializer(many=True)
    parent = serializers.PrimaryKeyRelatedField(queryset=Vendors.objects.all())

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
            raise ObjectDoesNotExist
        for data in contact_data:
            VendorContacts.objects.create(vendor=vendor, **data)

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

from rest_framework import serializers
from .models import Vendors, VendorContacts, VendorModuleNames, Modules
from django.shortcuts import get_object_or_404


class VendorsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Vendors
        fields = ('vendor_name',
                  'country',
                  'nda',
                  'parent_vendor',)


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


class VendorModulSerializer(serializers.ModelSerializer):
    serializers.RelatedField(source='module.id', read_only='True', many=True)

    class Meta:
        model = VendorModuleNames
        fields = ('module',)


class ModulesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Modules
        fields = ('module_name', )

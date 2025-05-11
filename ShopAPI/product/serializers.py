from rest_framework import serializers

from .models import *

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            'name',
            'slug'
        )

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'slug',
            'name'
        )

class ProductItemSerializer(serializers.ModelSerializer):
    configuration = serializers.SerializerMethodField()

    def get_configuration(self, obj):
        return obj.attribute\
           .filter(type_id = 'storage')\
           .values_list('option_name', flat=True)\
           .first()

    class Meta:
        model = ProductItem
        fields = (
            'product_id',
            'name',
            'color',
            'configuration',
            'price',
            'discount',
            'availability'
        )

class HeaderFooterSerializer(serializers.ModelSerializer):
    iphones = serializers.SerializerMethodField()
    macs = serializers.SerializerMethodField()

    def get_iphones(self, obj):
        iphones = Product.objects.filter(category_id=1).values_list('name', flat=True)
        return list(iphones)

    def get_macs(self, obj):
        macs = Product.objects.filter(category_id=2).values_list('name', flat=True)
        return list(macs)

    class Meta:
        model = Product
        fields = (
            'iphones',
            'macs'
        )

class FilterSerializer(serializers.ModelSerializer):
    class OptionSerializer(serializers.ModelSerializer):
        class Meta:
            model = AttributeOption
            fields = ('type_id', 'option_name')

    row = serializers.SerializerMethodField()

    def get_row(self, obj):
        category = self.context.get('category')
        qs = AttributeOption.objects.filter(category_id__slug=category,type_id=obj)
        return self.OptionSerializer(qs, many=True).data

    class Meta:
        model = AttributeType
        fields = ('id', 'type', 'row')

class FullProductItemSerializer(serializers.ModelSerializer):
    attributes = serializers.SerializerMethodField()
    configuration = serializers.SerializerMethodField()

    def get_configuration(self, obj):
        return obj.attribute\
           .filter(type_id = 'storage')\
           .values_list('option_name', flat=True)\
           .first()
    def get_attributes(self, obj:ProductItem):
        return {option.type_id.type: option.option_name for option in obj.attribute.all()}

    class Meta:
        model = ProductItem
        fields = (
            'product_id',
            'name',
            'color',
            'weight',
            'configuration',
            'price',
            'discount',
            'availability',
            'attributes',
            'specification'
        )

class ShortProductItemSerializer(serializers.ModelSerializer):
    configuration = serializers.SerializerMethodField()

    def get_configuration(self, obj):
        return obj.attribute\
           .filter(type_id = 'storage')\
           .values_list('option_name', flat=True)\
           .first()

    class Meta:
        model = ProductItem
        fields = (
            'name',
            'color',
            'configuration',
            'price',
            'discount',
            'availability'
        )

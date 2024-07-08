from rest_framework import serializers
from .models import Giveaway, Platform, Supplier


class GiveawaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Giveaway
        fields = '__all__'


class GiveawaySerializerPublic(serializers.ModelSerializer):
    class Meta:
        model = Giveaway
        fields = ['type',
                  'title',
                  'description',
                  'url',
                  'status',
                  'post_image',
                  'platforms']


class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = '__all__'


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'


class SupplierSerializerPublic(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'title']

from . import models
from rest_framework import serializers


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Properties
        fields = '__all__'

        read_only_fields = ['id', 'created_at', 'updated_at']

class WishlistSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Wishlist
        fields = '__all__'

        read_only_fields = ['id', 'created_at', 'updated_at']

class BookingsSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Bookings
        fields = '__all__'

        read_only_fields = ['id', 'created_at', 'updated_at']
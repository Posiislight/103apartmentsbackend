from . import models
from rest_framework import serializers
from .models import User, Bookings
class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Properties
        fields = '__all__'

        read_only_fields = ['id', 'created_at', 'updated_at']

class WishlistSerializer(serializers.ModelSerializer):
    property = PropertySerializer(read_only=True)
    class Meta:
        model = models.Wishlist
        fields = '__all__'
        read_only_fields = ['id','user', 'created_at', 'updated_at']

class BookingsSerializer(serializers.ModelSerializer):
    property_details = PropertySerializer(source='property', read_only=True)
    
    class Meta:
        model = models.Bookings
        fields = '__all__'

        read_only_fields = ['id','user', 'created_at', 'updated_at']
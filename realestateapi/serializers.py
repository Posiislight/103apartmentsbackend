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

class BookingMiniSerializer(serializers.ModelSerializer):
    property_details = PropertySerializer(many=True, read_only=True, source='bookings_set')

    class Meta:
        model = Bookings
        fields = ['id', 'property_details', 'booking_date', 'status']

class UserSerializer(serializers.ModelSerializer):
    bookings = BookingMiniSerializer(read_only=True)
    class Meta:
        model = models.User
        fields = '__all__'

class BookingsSerializer(serializers.ModelSerializer):
    property_details = PropertySerializer(source='property', read_only=True)
    user_details = UserSerializer(source='user',read_only=True)
    
    class Meta:
        model = models.Bookings
        fields = '__all__'

        read_only_fields = ['id','user', 'created_at', 'updated_at']
        
class RecentBookingSerializer(serializers.ModelSerializer):
    property = PropertySerializer()
    user = UserSerializer()
    class Meta:
        model = Bookings
        fields = ['id', 'property', 'user', 'booking_date', 'status']
        

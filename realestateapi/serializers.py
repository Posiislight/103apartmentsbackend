from . import models
from rest_framework import serializers
from .models import User, Bookings
from django.contrib.auth import authenticate,get_user_model
import logging

class PropertyImagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PropertyImages
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

class PropertySerializer(serializers.ModelSerializer):
    gallery_images = PropertyImagesSerializer(many=True, read_only=True, source='gallery_images')
    
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

User = get_user_model()
logger = logging.getLogger(__name__)  # Best practice: per-module logger

class AdminLoginSerializer(serializers.Serializer):
    username = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        try:
            user_obj = User.objects.get(username=username)
        except User.DoesNotExist:
            logger.warning(f"Login failed: user with email '{username}' does not exist.")
            raise serializers.ValidationError({"non_field_errors": ["Invalid credentials."]})

        if not user_obj.is_active:
            logger.warning(f"Login failed: inactive user '{username}'.")
            raise serializers.ValidationError({"non_field_errors": ["User account is disabled."]})

        # Note: make sure the authenticate() call matches your auth backend
        user = authenticate(request=self.context.get('request'), username=username, password=password)


        if not user:
            logger.warning(f"Login failed: authentication failed for email '{username}'.")
            raise serializers.ValidationError({"non_field_errors": ["Invalid credentials."]})


        logger.info(f"Admin login successful for '{username}'.")
        data["user"] = user
        return data
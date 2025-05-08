from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.middleware.csrf import get_token
from .models import Properties, Wishlist, User, Bookings
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from . import serializers

# AUTHENTICATION VIEWS

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        if password != confirm_password:
            return Response({"message": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.create_user(email=email, password=password, first_name=first_name, last_name=last_name)
            return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"message": "Logout successful"}, status=status.HTTP_200_OK)

class CSRFTokenView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        csrf_token = get_token(request)
        return Response({'csrfToken': csrf_token}, status=status.HTTP_200_OK)

# PROPERTY VIEWS

class PropertyListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        properties = Properties.objects.all()
        serializer = serializers.PropertySerializer(properties, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = serializers.PropertySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        property_id = request.data.get('id')
        try:
            property = Properties.objects.get(pk=property_id)
            serializer = serializers.PropertySerializer(property, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Properties.DoesNotExist:
            return Response({"message": "Property not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        property_id = request.data.get('id')
        try:
            property = Properties.objects.get(pk=property_id)
            property.delete()
            return Response({"message": "Property deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Properties.DoesNotExist:
            return Response({"message": "Property not found"}, status=status.HTTP_404_NOT_FOUND)

class PropertyDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            property = Properties.objects.get(pk=pk)
            serializer = serializers.PropertySerializer(property)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Properties.DoesNotExist:
            return Response({"message": "Property not found"}, status=status.HTTP_404_NOT_FOUND)

# WISHLIST

class WishlistView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        wishlist_items = Wishlist.objects.filter(user=user)
        serializer = serializers.WishlistSerializer(wishlist_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        property_id = request.data.get('property')
        try:
            Wishlist.objects.create(user=user, property_id=property_id)
            return Response({"message": "Added to wishlist"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# BOOKINGS

class BookingsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        bookings = Bookings.objects.filter(user=user)
        serializer = serializers.BookingsSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        serializer = serializers.BookingsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ADMIN VIEWS

class AdminDashboard(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        properties = Properties.objects.all()
        users = User.objects.all()
        featured_properties = Properties.objects.filter(is_featured=True)
        bookings = Bookings.objects.order_by('-booking_date')

        serialized_data = {
            'properties': serializers.PropertySerializer(properties, many=True).data,
            'users': serializers.UserSerializer(users, many=True).data,
            'featured_properties': serializers.PropertySerializer(featured_properties, many=True).data,
            'bookings': serializers.BookingsSerializer(bookings, many=True).data
        }
        return Response(serialized_data, status=status.HTTP_200_OK)

class AdminPropertyPage(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        properties = Properties.objects.all()
        serializer = serializers.PropertySerializer(properties, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request):
        property_id = request.data.get('id')
        try:
            property = Properties.objects.get(pk=property_id)
            serializer = serializers.PropertySerializer(property, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Properties.DoesNotExist:
            return Response({"message": "Property not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request):
        property_id = request.data.get('id')
        try:
            property = Properties.objects.get(pk=property_id)
            property.delete()
            return Response({"message": "Property deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        except Properties.DoesNotExist:
            return Response({"message": "Property not found"}, status=status.HTTP_404_NOT_FOUND)

class AdminUserPage(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all()
        serializer = serializers.UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class AdminBookingsPage(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        bookings = Bookings.objects.all()
        serializer = serializers.BookingsSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# HOME PAGE

class HomePage(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        properties = Properties.objects.all()
        serializer = serializers.PropertySerializer(properties, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

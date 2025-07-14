from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.middleware.csrf import get_token
from django.http import JsonResponse
from realestatebackend import settings
from .models import Properties, Wishlist, User, Bookings,PropertyImages
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser

from . import serializers

from datetime import datetime
import requests 
# AUTHENTICATION VIEWS

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        return Response({"message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        if password != confirm_password:
            return Response({"message": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
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
    permission_classes = [AllowAny]

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
            property = Properties.objects.get(pk=property_id)
            serializer = serializers.WishlistSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=user, property=property) 
                return Response({"message": "Added to wishlist"}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        user = request.user
        property_id = request.data.get('property')
        if not property_id:
            return Response({"error": "Property ID required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            property = Properties.objects.get(pk=property_id)
            wishlist = Wishlist.objects.get(user_id=user, property_id=property_id)
            wishlist.delete()
            return Response({"message": "Wishlist item deleted"}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"message": "Wishlist item not found"}, status=status.HTTP_404_NOT_FOUND)

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
        price = float(request.data.get('total_price'))
        check_out_date = request.data.get('check_out_date')
        check_in_date = request.data.get('check_in_date')
        property_id = request.data.get('property')
        property = Properties.objects.get(pk=property_id)  
        if not check_in_date or not check_out_date:
            return Response({"error": "Check-in and check-out dates are required"}, status=400)
        check_in = datetime.strptime(check_in_date, "%Y-%m-%d").date()
        check_out = datetime.strptime(check_out_date, "%Y-%m-%d").date()
        days = (check_out - check_in).days
        total_price = price*days

        
        if serializer.is_valid():
            serializer.save(user=user,total_price=total_price)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ADMIN VIEWS
class AdminDashboard(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        properties = Properties.objects.all()
        users = User.objects.all()
        featured_properties = Properties.objects.filter(is_featured=True)
        bookings = Bookings.objects.order_by('-booking_date')

        serialized_data = {
            'properties': serializers.PropertySerializer(properties, many=True).data,
            'users': serializers.UserSerializer(users, many=True).data,
            'featured_properties': serializers.PropertySerializer(featured_properties, many=True).data,
            'bookings': serializers.BookingsSerializer(bookings, many=True).data,
            'counts' : {
                'properties':properties.count(),
                'users': users.count(),
                'bookings':bookings.count(),
                'featured_properties':featured_properties.count(),
            }
            
            
        }
        return Response(serialized_data, status=status.HTTP_200_OK)

class AdminPropertyPage(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        properties = Properties.objects.all()
        serializer = serializers.PropertySerializer(properties, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    def post(self,request):
        serializer = serializers.PropertySerializer(data=request.data)
        if serializer.is_valid():
            property_instance=serializer.save()
            serializer.save()

            for image in request.FILES.getlist('gallery_images'):
                PropertyImages.objects.create(property=property_instance, image=image)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
# HOME PAGE

class HomePage(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        properties = Properties.objects.all()
        serializer = serializers.PropertySerializer(properties, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class BookingsDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        user = request.user
        booking = Bookings.objects.get(user=user,pk=pk)
        serializer = serializers.BookingsSerializer(booking)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PropertyBookingView(APIView):
    permission_classes = [AllowAny]

    def get(self,request,pk):
        booking = Bookings.objects.filter(property_id=pk)
        serializer = serializers.BookingsSerializer(booking,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FeaturedPropertyView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        properties = Properties.objects.filter(is_featured=True)
        serializer = serializers.PropertySerializer(properties, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class PayStackView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        user = request.user
        amount = request.data.get('total_price')
        email = request.data.get('username')
        if not amount or not email:
            return Response({"error": "Amount and email are required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            headers = {
                "Authorization": f'Bearer {settings.PAYSTACK_SECRET_KEY}',
                "Content-Type": "application/json"
            }

            data = {
                "email":email,
                "amount": int(float(amount) * 100)  # Convert to kobo
            }

            response = requests.post('https://api.paystack.co/transaction/initialize', headers=headers, json=data)
            if response.status_code != 200:
                return Response({"error": "Failed to initialize payment"}, status=response.status_code)
            return Response(response.json(), status=response.status_code)
        except Exception as e:
            print(request.data)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def get(self,request):
        try:
            reference = request.query_params.get('reference')
            headers = {
                'Authorization':f"Bearer {settings.PAYSTACK_SECRET_KEY}",
                'Content-type':'application/json'
            }
            url = f'https://api.paystack.co/transaction/verify/{reference}'
            response = requests.get(url,headers=headers)
            return Response(response.json(),status=response.status_code)
        except Exception as e:
            return Response({"error":str(e)},status=response.status_code)


class UserDetailsView(APIView):
    def get(self,request):
        user = request.user
        try:
            serializer = serializers.UserSerializer(user)
            return Response(serializer.data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)



class CalculateBookingTotalPriceView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        property_id = request.query_params.get('property_id')
        check_in_date = request.query_params.get('check_in_date')
        check_out_date = request.query_params.get('check_out_date')

        if not property_id or not check_in_date or not check_out_date:
            return Response({"error": "property_id, check_in_date, and check_out_date are required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            property_obj = Properties.objects.get(pk=property_id)
            check_in = datetime.strptime(check_in_date, "%Y-%m-%d").date()
            check_out = datetime.strptime(check_out_date, "%Y-%m-%d").date()
            days = (check_out - check_in).days
            if days <= 0:
                return Response({"error": "Check-out date must be after check-in date."}, status=status.HTTP_400_BAD_REQUEST)
            total_price = property_obj.price * days
            return Response({"total_price": total_price, "days": days, "price_per_day": property_obj.price}, status=status.HTTP_200_OK)
        except Properties.DoesNotExist:
            return Response({"error": "Property not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class RecentBookingsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        bookings = Bookings.objects.select_related('property', 'user').order_by('-booking_date')  # latest 10
        serializer = serializers.RecentBookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AdminPropertyDetailView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, pk):
        try:
            return Properties.objects.get(pk=pk)
        except Properties.DoesNotExist:
            return None

    def put(self, request, pk):
        property = self.get_object(pk)
        if not property:
            return Response({"error": "Property not found"}, status=status.HTTP_404_NOT_FOUND)
        main_image = request.FILES.get("image")
        gallery_images = request.FILES.getlist("gallery_images")

        
        serializer = serializers.PropertySerializer(property, data=request.data)
        if serializer.is_valid():
            property_instance=serializer.save()
            serializer.save()

            for image in request.FILES.getlist('gallery_images'):
                PropertyImages.objects.create(property=property_instance, image=image)

            return Response({"message":"property deleted successfuly"},status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


    def delete(self,request,pk):
        property = self.get_object(pk)
        if not property:
            return Response({"message":"property doesnt exist"},status=status.HTTP_404_NOT_FOUND)
        property.delete()
        return Response({"message":"property successfuly deleted"},status=status.HTTP_204_NO_CONTENT)
    
class AdminBookingsPage(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        bookings = Bookings.objects.all()
        serializer = serializers.BookingsSerializer(bookings, many=True)

        # Prepare cleaned/flattened data for frontend
        serializer_data = [
            {
                "id": booking["id"],
                "propertyTitle": booking["property_details"]["title"],
                "propertyImage": booking["property_details"]["image"],
                "client": f"{booking['user_details']['first_name']} {booking['user_details']['last_name']}",
                "email": booking["user_details"]["username"],
                "check_in": booking["check_in_date"],
                "check_out": booking["check_out_date"],
                "booking_date":booking["booking_date"],
                
            }
            for booking in serializer.data
        ]

        return Response(serializer_data, status=status.HTTP_200_OK)

class AdminUserPage(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        users = User.objects.all()

        serializer_data = [
            {
                "name": f"{user.first_name} {user.last_name}",
                "email": user.username,
                "total_bookings": user.booking.count()  # If no related_name is set
            }
            for user in users
        ]

        return Response(serializer_data)
    
class AdminLoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = serializers.AdminLoginSerializer(data=request.data, context={'request': request})

        
        if serializer.is_valid():
            user = serializer.validated_data['user']  # Get user from validated_data
            return JsonResponse(
                {
                    "user":{
                        "id": user.id,
                        "email": user.username,
                        "is_admin": user.is_admin,
                    }
                }
            )
        else:
            print(request.data)
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AdminRegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = serializers.UserSerializer(data=request.data)

        if serializer.is_valid():
            validated_data = serializer.validated_data
            password = validated_data.get('password')
            confirm_password = request.data.get('confirm_password')  # Still coming from raw data

            if password != confirm_password:
                return Response({"message": "The passwords don't match"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.create_superuser(
                username=validated_data.get('username'),
                    password=password,
                    
                    first_name=validated_data.get('first_name'),
                    last_name=validated_data.get('last_name')
                )
                return Response({"message": "Admin created successfully"}, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({"message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
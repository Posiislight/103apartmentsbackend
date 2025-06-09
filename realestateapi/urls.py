from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('csrf-token/', views.CSRFTokenView.as_view(), name='csrf-token'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),

    # Public
    path('home/', views.HomePage.as_view(), name='home'),
    path('properties/', views.PropertyListView.as_view(), name='property-list'),
    path('property/<int:pk>/', views.PropertyDetailView.as_view(), name='property-detail'),

    # Wishlist & Bookings (user-authenticated)
    path('wishlist/', views.WishlistView.as_view(), name='wishlist'),
    path('bookings/', views.BookingsView.as_view(), name='bookings'),
    path('bookings/<int:pk>/', views.BookingsDetailView.as_view(), name='booking-detail'),
    path('property/<int:pk>/booking/', views.PropertyBookingView.as_view(), name='property-booking'),

    # Admin Dashboard Pages
    path('admin/dashboard/', views.AdminDashboard.as_view(), name='admin-dashboard'),
    path('admin/properties/', views.AdminPropertyPage.as_view(), name='admin-properties'),
    path('admin/users/', views.AdminUserPage.as_view(), name='admin-users'),
    path('admin/bookings/', views.AdminBookingsPage.as_view(), name='admin-bookings'),
]


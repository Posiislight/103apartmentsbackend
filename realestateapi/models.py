from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, username, password=None, first_name=None, last_name=None):
        if not username:
            raise ValueError('Users must have an email address')
        if not password:
            raise ValueError('Users must have a password')
        username = self.normalize_email(username)
        user = self.model(username=username, first_name=first_name, last_name=last_name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, first_name=None, last_name=None):
        user = self.create_user(username, password, first_name, last_name)
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    username = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    confirm_password = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name','password']

    objects = UserManager()

    def __str__(self):
        return self.username

class Properties(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    area = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='properties/', null=True, blank=True)
    is_wishlist = models.BooleanField(default=False)

    def __str__(self):
        return self.title

class PropertyImages(models.Model):
    property = models.ForeignKey(Properties, on_delete=models.CASCADE,related_name='property_images')
    image = models.ImageField(upload_to='properties/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.property.title} - {self.image.name}"

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    property = models.ForeignKey(Properties, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'property')

    def __str__(self):
        return f"{self.user.username} - {self.property.title}"

class Bookings(models.Model):
    choices = [
        ('Pending','Pending'),
        ('Completed','Completed'),
        ('Cancelled','Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='booking')
    property = models.ForeignKey(Properties, on_delete=models.CASCADE,related_name='property')
    booking_date = models.DateTimeField(auto_now_add=True)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=15,choices=choices,default='Pending')

    def __str__(self):
        return f"{self.user.username} - {self.property.title} - {self.check_in_date} to {self.check_out_date}"
    

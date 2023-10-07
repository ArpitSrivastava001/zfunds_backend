from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from base.models import BaseModel


class UserManager(BaseUserManager):
    def create_user(self, mobile_number, password=None, **extra_fields):
        if not mobile_number:
            raise ValueError('The Mobile Number must be set')
        user = self.model(mobile_number=mobile_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        return self.create_user(mobile_number, password, **extra_fields)


class UserType:
    ADVISOR = 1
    CLIENT = 2


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    user_type_choices = (
        (None, 'Select User Type'),
        (UserType.ADVISOR, 'Advisor'),
        (UserType.CLIENT, 'Client'),
    )
    mobile_number = PhoneNumberField(unique=True)
    name = models.CharField(max_length=100)
    user_type = models.IntegerField(choices=user_type_choices, default=None, null=True)
    otp_secret_key = models.CharField(max_length=16, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    otp_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'mobile_number'

    def __str__(self):
        return str(self.mobile_number)
from django.db import models

# Create your models here.
import random
import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.mail import send_mail


class MyUserManager(BaseUserManager):
    def create_user(self, email, password, name, phone, dob, college):
        if not email:
            raise ValueError("Email ID is required")
        if not name:
            raise ValueError("Full Name is required")
        if not phone:
            raise ValueError("Phone No. is required")
        if not dob:
            raise ValueError("DOB is required")
        if not college:
            raise ValueError("College Name is required")
        if not password:
            raise ValueError("Password is required")

        user = self.model(email=email, name=name, phone=phone, dob=dob, college=college)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, name, phone, dob, college):
        user = self.create_user(email, password, name, phone, dob, college)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    email = models.EmailField(name="email", verbose_name="Email Address", max_length=100, unique=True)
    name = models.CharField(name="name", verbose_name="Full Name", max_length=100)
    phone = models.IntegerField(name="phone", verbose_name="Phone Number", unique=True)
    dob = models.DateField(name="dob", verbose_name="Date of Birth")
    profile_pic = models.TextField(name="profile", verbose_name="Profile Picture", blank=True, null=True)
    college = models.CharField(name="college", verbose_name="College Name", max_length=100)
    exam_roll = models.CharField(name="roll", verbose_name="Exam Roll Number", max_length=15, blank=True, null=True)

    otp = models.CharField(verbose_name="otp", max_length=6, blank=True, null=True)
    otp_expire = models.DateTimeField(name="otp_expire", verbose_name="OTP Expire", blank=True, null=True)
    verified = models.CharField(name="verified", verbose_name="Verified", max_length=1, default="N")

    date_joined = models.DateTimeField(name="date_joined", verbose_name="Date Joined", auto_now_add=True)
    last_login = models.DateTimeField(name="last_login", verbose_name="Last Login", auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "phone", "dob", "college"]

    objects = MyUserManager()

    def generate_otp(self):
        try:
            self.otp = str(random.randint(100000, 999999))
            self.otp_expire = timezone.now() + datetime.timedelta(hours=1)
            self.save()
            return True
        except Exception as e:
            return False

    def send_otp_in_mail(self):
        send_mail(
            'Account verification',
             'Your OTP for verifying account of ivMentor is: ' + self.otp+". \n\nThankyou for showing interest in ivMentor!" ,
            'ivmentor02021@gmail.com',
            [self.email,],
            fail_silently=False,
        )






    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

class feed(models.Model):
    name=models.CharField(max_length=100)
    email=models.EmailField(max_length=100)
    feedback=models.TextField()

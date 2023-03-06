from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import *


class MyUserAdmin(admin.ModelAdmin):
    readonly_fields = ("date_joined", "last_login", "otp_expire")
    list_display = ("email", "name", "phone")


admin.site.register(MyUser, MyUserAdmin)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm

from .models import User

# Register your models here.
class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User

class CustomUserAdmin(UserAdmin):
    form = UserChangeForm

    fieldsets = UserAdmin.fieldsets


admin.site.register(User,CustomUserAdmin)
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm
from .models import Account

class AccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_type', 'account_number', 'balance') 
    search_fields = ('account_number', 'user__username') 

admin.site.register(Account, AccountAdmin)

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm 
    model = User
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


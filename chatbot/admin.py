from django.contrib import admin
from .models import ChatSession 
# Register your models here.
admin.site.register(ChatSession)

from django.contrib import admin
from django import forms
from .models import AdminUser

class AdminUserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    
    class Meta:
        model = AdminUser
        fields = '__all__'
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])  # Hashes automatically
        if commit:
            user.save()
        return user

@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    form = AdminUserForm

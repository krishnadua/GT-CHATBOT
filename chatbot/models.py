from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class LoginUser(models.Model):
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    google_id = models.CharField(max_length=100, blank=True, null=True)
    is_google_user = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    password = models.CharField(max_length=128, blank=True, null=True)
    last_login = models.DateTimeField(null=True, blank=True)  # NEW: Add this to fix the error

    def __str__(self):
        return self.username

    def is_authenticated(self):
        return True

class ChatSession(models.Model):
    username = models.CharField(max_length=100, unique=True)
    history = models.JSONField(default=list)  # List of {"role": "user/assistant", "content": str, "action_html": str|null}
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.username

    def add_exchange(self, user_msg, ai_reply, action_html=None):
        self.history.append({"role": "user", "content": user_msg})
        self.history.append({"role": "assistant", "content": ai_reply, "action_html": action_html})
        self.save()
    
    def set_password(self, raw_password):
        """Hash and set the password."""
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        """Verify raw password against hashed password."""
        return check_password(raw_password, self.password)

class AdminUser(models.Model):
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=128)  # Hashed password
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.save()

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)
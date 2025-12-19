from django.urls import path
from . import views
from django.conf.urls import handler404
from django.views.defaults import page_not_found

urlpatterns = [
    path('', views.index, name='chatbot_index'),        # Main chat page
    path('chat/', views.chat, name='chatbot_api'),      # AJAX endpoint for messages
    # path('run_auto_open/', views.run_auto_open, name='run_auto_open'),
    path('chat/<str:username>/', views.chat, name='chat'),
   path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('admin-show-chat/', views.admin_show_chat, name='admin_show_chat'),
    path('admin-edit-file/', views.admin_edit_file, name='admin_edit_file'),
   path("admin_chat_details/<str:username>/", views.admin_chat_details, name="admin_chat_details"),
    path('validate-username/', views.validate_username, name='validate_username'),
   path('log_call/', views.log_call, name='log_call'),

   path('login/', views.login_view, name='login'),  # Renders login.html
    path('auth/google/login/', views.google_login_view, name='google_login'),
    path('auth/google/callback/', views.google_callback_view, name='google_callback'),
    path('logout/', views.logout_view, name='logout'),  # Clears session
    path('whatsapp/webhook/', views.whatsapp_webhook, name='whatsapp_webhook'),
    # path('whatsapp/', views.whatsapp_test, name='whatsapp_test'),
    # path('test-send-message/', views.test_send_message, name='test_send_message'),
    # path('test-whatsapp-send/', views.test_whatsapp_send, name='test_whatsapp_send'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),  # Privacy Policy page
    path('terms/', views.terms_conditions, name='terms_conditions'),  # Terms & Conditions page
    # Add this URL to urls.py (add it inside the urlpatterns list, e.g., after the existing test_send_message path)

path('send-whatsapp-response/', views.send_whatsapp_chatbot_response, name='send_whatsapp_chatbot_response'),

]

handler404 = "golden_tree_ai.views.custom_404"
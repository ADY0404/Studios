from django.urls import path
from django.contrib.auth import views as auth_views
from apps.accounts import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('settings/', views.account_settings_view, name='settings'),
    path('delete/', views.delete_account_view, name='delete'),
    
    # Email Confirmation
    path('confirm-email/<uidb64>/<token>/', views.confirm_email_view, name='confirm_email'),
    path('resend-confirmation/', views.resend_confirmation_view, name='resend_confirmation'),
    
    # Password Reset
    path(
        'password-reset/', 
        auth_views.PasswordResetView.as_view(
            template_name='accounts/password_reset.html',
            email_template_name='accounts/password_reset_email.txt',
            subject_template_name='accounts/password_reset_subject.txt',
            success_url='/auth/password-reset/done/'
        ), 
        name='password_reset'
    ),
    path(
        'password-reset/done/', 
        auth_views.PasswordResetDoneView.as_view(
            template_name='accounts/password_reset_done.html'
        ), 
        name='password_reset_done'
    ),
    path(
        'reset/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/password_reset_confirm.html',
            success_url='/auth/reset/done/'
        ), 
        name='password_reset_confirm'
    ),
    path(
        'reset/done/', 
        auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/password_reset_complete.html'
        ), 
        name='password_reset_complete'
    ),
]

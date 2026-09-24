from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.forms import RegistrationForm, AccountSettingsForm
from apps.profiles.forms import UsernameChangeForm

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:overview')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Custom profile display name/username if provided
            username = form.cleaned_data.get('username')
            if hasattr(user, 'profile'):
                user.profile.username = username
                user.profile.display_name = form.cleaned_data.get('display_name') or username
                user.profile.save()
            login(request, user)
            from apps.accounts.emails import send_account_confirmation_email
            send_account_confirmation_email(user)
            messages.success(request, f"Welcome to LinkStudio, {user.profile.display_name}! Your creator profile is ready.")
            return redirect('dashboard:overview')
    else:
        form = RegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('/admin/')
        return redirect('dashboard:overview')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            # Administrators strictly use the Django Admin Console
            if user.is_staff or user.is_superuser:
                messages.info(request, f"Signed in as administrator ({user.username}). Welcome to the Admin Console.")
                return redirect('/admin/')

            display_name = user.profile.display_name if hasattr(user, 'profile') else user.username
            messages.success(request, f"Welcome back, {display_name}!")
            next_url = request.GET.get('next')
            if next_url and not next_url.startswith('/admin') and 'dashboard' in next_url:
                return redirect(next_url)
            return redirect('dashboard:overview')
        else:
            messages.error(request, "Invalid username/email or password.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    if request.method in ['POST', 'GET']:
        logout(request)
        messages.info(request, "You have been signed out.")
        return redirect('accounts:login')


@login_required
def account_settings_view(request):
    if request.user.is_staff or request.user.is_superuser:
        messages.info(request, "Administrator accounts are managed via the Django Admin Console.")
        return redirect('/admin/')

    user = request.user
    profile = user.profile
    
    email_form = AccountSettingsForm(instance=user)
    username_form = UsernameChangeForm(current_profile=profile, initial={'username': profile.username})
    password_form = PasswordChangeForm(user=user)

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_email':
            email_form = AccountSettingsForm(request.POST, instance=user)
            if email_form.is_valid():
                email_form.save()
                messages.success(request, "Email address updated successfully.")
                return redirect('accounts:settings')
                
        elif action == 'update_username':
            username_form = UsernameChangeForm(current_profile=profile, data=request.POST)
            if username_form.is_valid():
                new_username = username_form.cleaned_data['username']
                profile.username = new_username
                profile.save(update_fields=['username'])
                # Also synchronize User.username
                user.username = new_username
                user.save(update_fields=['username'])
                messages.success(request, f"Username changed to @{new_username}!")
                return redirect('accounts:settings')
                
        elif action == 'change_password':
            password_form = PasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Your password was changed successfully.")
                return redirect('accounts:settings')
            else:
                messages.error(request, "Please correct the password errors below.")

    return render(request, 'accounts/settings.html', {
        'email_form': email_form,
        'username_form': username_form,
        'password_form': password_form,
        'profile': profile
    })


@login_required
def delete_account_view(request):
    if request.method == 'POST':
        confirmation = request.POST.get('confirm_delete')
        if confirmation == request.user.username:
            user = request.user
            logout(request)
            user.delete()
            messages.success(request, "Your account and all associated profile data have been permanently deleted.")
            return redirect('accounts:register')
        else:
            messages.error(request, "Confirmation username does not match. Account deletion cancelled.")
            return redirect('accounts:settings')
    return redirect('accounts:settings')

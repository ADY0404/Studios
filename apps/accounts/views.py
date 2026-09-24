from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from apps.accounts.forms import RegistrationForm, AccountSettingsForm
from apps.profiles.forms import UsernameChangeForm
from apps.profiles.models import Profile, Appearance
from apps.accounts.emails import send_email_verification_email


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:overview')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Require email confirmation before account can log in
            user.is_active = False
            user.save()

            # Profile display name/username
            username = form.cleaned_data.get('username')
            display_name = form.cleaned_data.get('display_name') or username
            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults={
                    'username': username,
                    'display_name': display_name,
                    'public_email': user.email,
                    'is_email_verified': False
                }
            )
            if not created:
                profile.username = username
                profile.display_name = display_name
                profile.public_email = user.email
                profile.is_email_verified = False
                profile.save(update_fields=['username', 'display_name', 'public_email', 'is_email_verified'])
            Appearance.objects.get_or_create(profile=profile)

            # Send verification link via email
            send_email_verification_email(user, request)

            messages.success(request, f"Account created for @{username}! Please check your email inbox to confirm your address before logging in.")
            return render(request, 'accounts/confirm_email_sent.html', {
                'email': user.email,
                'display_name': display_name
            })
    else:
        form = RegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def confirm_email_view(request, uidb64, token):
    """
    Activates user account once they click the verification link in their email.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save(update_fields=['is_active'])
        if hasattr(user, 'profile'):
            user.profile.is_email_verified = True
            user.profile.save(update_fields=['is_email_verified'])
        messages.success(request, "Your email has been confirmed successfully! You can now sign in to your account.")
        return redirect('accounts:login')
    else:
        messages.error(request, "This confirmation link is invalid or has expired. Please request a new confirmation email below.")
        return redirect('accounts:resend_confirmation')


def resend_confirmation_view(request):
    """
    Allows unconfirmed users to request a fresh confirmation email.
    """
    unconfirmed_email = request.GET.get('email', '')
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        user = User.objects.filter(email__iexact=email).first()
        if user:
            if user.is_active and getattr(getattr(user, 'profile', None), 'is_email_verified', False):
                messages.info(request, "Your account email is already verified. You can sign in.")
                return redirect('accounts:login')
            send_email_verification_email(user, request)
            messages.success(request, f"A fresh confirmation email has been sent to {email}. Please check your inbox.")
            return render(request, 'accounts/confirm_email_sent.html', {'email': email})
        else:
            messages.info(request, f"If an account with {email} is pending confirmation, a link has been sent.")
            return redirect('accounts:login')

    return render(request, 'accounts/resend_confirmation.html', {'unconfirmed_email': unconfirmed_email})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:overview')

    unconfirmed_email = None

    if request.method == 'POST':
        login_input = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # Support sign in by either username or email
        user_obj = None
        if '@' in login_input:
            user_obj = User.objects.filter(email__iexact=login_input).first()
        else:
            user_obj = User.objects.filter(username__iexact=login_input).first()

        # Check if user exists and password is correct
        if user_obj and user_obj.check_password(password):
            # Check email confirmation status (staff and superuser accounts can bypass)
            is_verified = user_obj.is_active and (
                user_obj.is_staff or 
                user_obj.is_superuser or 
                getattr(getattr(user_obj, 'profile', None), 'is_email_verified', True)
            )

            if not is_verified:
                unconfirmed_email = user_obj.email
                messages.error(request, "You cannot log in until you confirm your email. Please check your inbox or resend the verification email below.")
                return render(request, 'accounts/login.html', {
                    'unconfirmed_email': unconfirmed_email,
                })

            # User is verified — log in
            login(request, user_obj)

            display_name = user_obj.profile.display_name if hasattr(user_obj, 'profile') else user_obj.username
            messages.success(request, f"Welcome back, {display_name}!")
            next_url = request.GET.get('next')
            if next_url and 'dashboard' in next_url:
                return redirect(next_url)
            return redirect('dashboard:overview')
        else:
            # Fall back to standard authenticate for edge cases
            user = authenticate(request, username=login_input, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard:overview')
            messages.error(request, "Invalid username/email or password.")

    return render(request, 'accounts/login.html', {
        'unconfirmed_email': unconfirmed_email,
    })


def logout_view(request):
    if request.method in ['POST', 'GET']:
        logout(request)
        messages.info(request, "You have been signed out.")
        return redirect('accounts:login')


@login_required
def account_settings_view(request):
    user = request.user
    # Ensure profile exists (auto-provision for admin if needed)
    profile, _ = Profile.objects.get_or_create(
        user=user,
        defaults={
            'username': user.username,
            'display_name': user.get_full_name() or user.username,
            'public_email': user.email
        }
    )
    
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

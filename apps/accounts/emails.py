import logging
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse

logger = logging.getLogger(__name__)


def send_email_verification_email(user, request=None):
    """
    Sends an email verification link to a user.
    The account cannot be logged into until this link is clicked.
    Wrapped in try/except so email delivery errors never crash the request.
    """
    recipient = user.email
    if not recipient:
        return False

    token = default_token_generator.make_token(user)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    path = reverse('accounts:confirm_email', kwargs={'uidb64': uidb64, 'token': token})

    if request:
        confirmation_url = request.build_absolute_uri(path)
    else:
        # Fallback for tasks or scripts without request context
        base_host = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
        confirmation_url = f"{base_host.rstrip('/')}{path}"

    display_name = getattr(getattr(user, 'profile', None), 'display_name', None) or user.username
    subject = "Confirm your LinkStudio email address"
    message = (
        f"Hi {display_name},\n\n"
        f"Thank you for signing up for LinkStudio!\n\n"
        f"Please confirm your email address by clicking the link below to activate your account:\n\n"
        f"{confirmation_url}\n\n"
        f"This confirmation link will expire in 24 hours.\n\n"
        f"If you did not register for a LinkStudio account, you can safely ignore this email.\n\n"
        f"Best regards,\nLinkStudio Team"
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'LinkStudio <noreply@linkstudio.app>'),
            recipient_list=[recipient],
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send email verification for user {user.username} ({user.id}): {e}")
        return False


def send_account_confirmation_email(user):
    """
    Legacy welcome notification helper.
    """
    return send_email_verification_email(user)

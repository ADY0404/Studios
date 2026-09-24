import logging
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_account_confirmation_email(user):
    """
    Sends an account welcome / confirmation email to the newly registered user.
    Wrapped in try/except so email delivery errors never block registration.
    """
    recipient = user.email
    if not recipient:
        return False

    display_name = getattr(getattr(user, 'profile', None), 'display_name', None) or user.username
    subject = f"Welcome to LinkStudio, {display_name}!"
    message = (
        f"Hi {display_name},\n\n"
        f"Thank you for joining LinkStudio! Your creator account and public link-in-bio page are ready.\n\n"
        f"Username: @{user.username}\n"
        f"Dashboard: /dashboard/\n"
        f"Public Bio: /{user.username}/\n\n"
        f"Start by adding your links, connecting your social handles, and setting up booking availability in your dashboard.\n\n"
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
        logger.error(f"Failed to send confirmation email for user {user.username} ({user.id}): {e}")
        return False


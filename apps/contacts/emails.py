import logging
from django.conf import settings
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)


def send_contact_submission_email(submission):
    """
    Sends an email notification to the creator when a new contact submission is received.
    Includes reply_to set to visitor's email so creator can hit reply directly.
    Wraps the send in try/except so failure never interrupts user flow.
    """
    profile = submission.profile
    recipient = profile.public_email or (profile.user.email if profile.user else None)
    if not recipient:
        return False

    subject = f"New Contact Message from {submission.name}"
    message = (
        f"Hi {profile.display_name},\n\n"
        f"You have received a new contact message on your LinkStudio page.\n\n"
        f"From: {submission.name}\n"
        f"Email: {submission.email}\n"
        f"Phone: {submission.phone or 'N/A'}\n"
        f"Date: {submission.created_at.strftime('%b %d, %Y at %H:%M UTC')}\n\n"
        f"Message:\n{submission.message}\n\n"
        f"You can reply directly to this email to respond to {submission.name} ({submission.email}).\n\n"
        f"Best regards,\nLinkStudio"
    )

    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'LinkStudio <noreply@linkstudio.app>')
        reply_to_list = [submission.email] if submission.email else None
        email_msg = EmailMessage(
            subject=subject,
            body=message,
            from_email=from_email,
            to=[recipient],
            reply_to=reply_to_list,
        )
        email_msg.send(fail_silently=False)
        return True
    except Exception as e:
        logger.error(f"Failed to send contact notification email for submission {submission.id}: {e}")
        return False

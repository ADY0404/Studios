import logging
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_booking_requested_email(booking):
    """
    Sends an email notification to the creator when a new booking is requested.
    Wraps the send in try/except so failure never interrupts user flow.
    """
    profile = booking.profile
    recipient = profile.public_email or (profile.user.email if profile.user else None)
    if not recipient:
        return False

    subject = f"New Booking Request: {booking.service.title} from {booking.visitor_name}"
    message = (
        f"Hi {profile.display_name},\n\n"
        f"You have received a new booking request for '{booking.service.title}'.\n\n"
        f"Visitor: {booking.visitor_name}\n"
        f"Email: {booking.visitor_email}\n"
        f"Phone: {booking.visitor_phone or 'N/A'}\n"
        f"Scheduled Time: {booking.start_time.strftime('%b %d, %Y at %H:%M UTC')}\n"
        f"Notes: {booking.notes or 'None'}\n\n"
        f"Log in to your dashboard to review and manage this booking.\n\n"
        f"Best regards,\nLinkStudio"
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
        logger.error(f"Failed to send booking requested email for booking {booking.id}: {e}")
        return False


def send_booking_status_update_email(booking):
    """
    Sends an email to the visitor when their booking status changes to confirmed, rejected, or cancelled.
    Wraps the send in try/except so failure never interrupts user flow.
    """
    if booking.status not in ('confirmed', 'rejected', 'cancelled'):
        return False

    recipient = booking.visitor_email
    if not recipient:
        return False

    status_display = booking.get_status_display()
    subject = f"Your Booking for '{booking.service.title}' is {status_display}"
    message = (
        f"Hi {booking.visitor_name},\n\n"
        f"Your booking request for '{booking.service.title}' with {booking.profile.display_name} has been {status_display.lower()}.\n\n"
        f"Details:\n"
        f"Service: {booking.service.title}\n"
        f"Scheduled Time: {booking.start_time.strftime('%b %d, %Y at %H:%M UTC')}\n"
    )
    if booking.status == 'confirmed' and booking.service.instructions:
        message += f"\nInstructions from Creator:\n{booking.service.instructions}\n"

    message += "\nThank you for using LinkStudio!\n"

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
        logger.error(f"Failed to send booking status email for booking {booking.id}: {e}")
        return False


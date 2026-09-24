import logging
from django.conf import settings
from django.core.mail import EmailMessage

logger = logging.getLogger(__name__)


def send_booking_requested_email(booking):
    """
    Sends an email notification to the creator when a new booking is requested.
    Sets reply_to to visitor email so creator can reply directly.
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
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'LinkStudio <noreply@linkstudio.app>')
        reply_to = [booking.visitor_email] if booking.visitor_email else None
        email_msg = EmailMessage(
            subject=subject,
            body=message,
            from_email=from_email,
            to=[recipient],
            reply_to=reply_to,
        )
        email_msg.send(fail_silently=False)
        return True
    except Exception as e:
        logger.error(f"Failed to send booking requested email for booking {booking.id}: {e}")
        return False


def send_booking_receipt_to_visitor(booking):
    """
    Sends an acknowledgment receipt to the visitor when they submit a booking request.
    Wraps the send in try/except so failure never interrupts user flow.
    """
    recipient = booking.visitor_email
    if not recipient:
        return False

    creator_name = booking.profile.display_name
    creator_email = booking.profile.public_email or (booking.profile.user.email if booking.profile.user else None)

    subject = f"Booking Request Received: {booking.service.title} with {creator_name}"
    message = (
        f"Hi {booking.visitor_name},\n\n"
        f"Thank you for requesting an appointment for '{booking.service.title}' with {creator_name}.\n\n"
        f"Scheduled Time: {booking.start_time.strftime('%b %d, %Y at %H:%M UTC')}\n"
        f"Status: Pending Confirmation\n\n"
        f"{creator_name} has been notified and will review your request. You will receive another email as soon as your booking is confirmed.\n\n"
        f"Best regards,\nLinkStudio"
    )

    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'LinkStudio <noreply@linkstudio.app>')
        reply_to = [creator_email] if creator_email else None
        email_msg = EmailMessage(
            subject=subject,
            body=message,
            from_email=from_email,
            to=[recipient],
            reply_to=reply_to,
        )
        email_msg.send(fail_silently=False)
        return True
    except Exception as e:
        logger.error(f"Failed to send booking receipt to visitor for booking {booking.id}: {e}")
        return False


def send_booking_status_update_email(booking):
    """
    Sends an email to the visitor when their booking status changes to confirmed, rejected, or cancelled.
    Sets reply_to to creator's email so visitor can reply directly.
    Wraps the send in try/except so failure never interrupts user flow.
    """
    if booking.status not in ('confirmed', 'rejected', 'cancelled'):
        return False

    recipient = booking.visitor_email
    if not recipient:
        return False

    creator_name = booking.profile.display_name
    creator_email = booking.profile.public_email or (booking.profile.user.email if booking.profile.user else None)

    status_display = booking.get_status_display()
    subject = f"Your Booking for '{booking.service.title}' is {status_display}"
    message = (
        f"Hi {booking.visitor_name},\n\n"
        f"Your booking request for '{booking.service.title}' with {creator_name} has been {status_display.lower()}.\n\n"
        f"Details:\n"
        f"Service: {booking.service.title}\n"
        f"Scheduled Time: {booking.start_time.strftime('%b %d, %Y at %H:%M UTC')}\n"
    )
    if booking.status == 'confirmed' and booking.service.instructions:
        message += f"\nInstructions from Creator:\n{booking.service.instructions}\n"

    message += "\nThank you for using LinkStudio!\n"

    try:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'LinkStudio <noreply@linkstudio.app>')
        reply_to = [creator_email] if creator_email else None
        email_msg = EmailMessage(
            subject=subject,
            body=message,
            from_email=from_email,
            to=[recipient],
            reply_to=reply_to,
        )
        email_msg.send(fail_silently=False)
        return True
    except Exception as e:
        logger.error(f"Failed to send booking status email for booking {booking.id}: {e}")
        return False

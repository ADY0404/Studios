import re
from django.core.exceptions import ValidationError

RESERVED_USERNAMES = {
    'admin', 'administrator', 'root', 'sysadmin', 'system',
    'login', 'logout', 'signin', 'signout', 'signup', 'register',
    'dashboard', 'settings', 'account', 'accounts', 'profile', 'profiles',
    'api', 'auth', 'media', 'static', 'assets', 'public',
    'links', 'link', 'bookings', 'booking', 'contacts', 'contact',
    'appearance', 'theme', 'themes', 'terms', 'privacy', 'help',
    'support', 'about', 'blog', 'explore', 'discover', 'password-reset',
    'password_reset', 'checkout', 'billing', 'pricing', 'vcf', 'save-contact',
    'favicon', 'favicon.ico'
}

def validate_username(value):
    """
    Validates username format, uniqueness, and ensures it's not a reserved keyword.
    """
    if not value:
        raise ValidationError("Username cannot be empty.")
        
    value_lower = value.strip().lower()
    
    if len(value_lower) < 3:
        raise ValidationError("Username must be at least 3 characters long.")
    if len(value_lower) > 30:
        raise ValidationError("Username cannot exceed 30 characters.")
        
    if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9_.-]*[a-zA-Z0-9]$', value):
        raise ValidationError(
            "Username can only contain letters, numbers, hyphens, underscores, and dots, "
            "and cannot start or end with a symbol."
        )
        
    if value_lower in RESERVED_USERNAMES:
        raise ValidationError(f"'{value}' is a reserved platform keyword and cannot be used.")
        
    return value

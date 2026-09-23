from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from apps.accounts.validators import validate_username

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    username = models.CharField(
        max_length=30, 
        unique=True, 
        db_index=True,
        validators=[validate_username],
        help_text="Unique creator handle used for your public page URL (e.g. /username/)"
    )
    display_name = models.CharField(max_length=80, help_text="Public creator or brand name")
    bio = models.TextField(max_length=500, blank=True, help_text="Short bio displayed on your profile")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    location = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True, help_text="Primary personal or company website")
    public_email = models.EmailField(blank=True, help_text="Public email for inquiries and vCard")
    phone = models.CharField(max_length=30, blank=True, help_text="Public phone number for vCard")
    
    show_contact_form = models.BooleanField(
        default=True, 
        help_text="Allow visitors to submit their contact info directly from your profile"
    )
    show_save_contact = models.BooleanField(
        default=True, 
        help_text="Show 'Save My Contact' (.vcf) button on your profile"
    )
    is_public = models.BooleanField(
        default=True, 
        help_text="Whether your profile is accessible publicly"
    )
    
    title_tagline = models.CharField(max_length=100, blank=True, help_text="Short headline (e.g. 'Founder & Designer' or 'Music Producer')")
    is_verified = models.BooleanField(default=True, help_text="Show verified creator badge")
    
    # Analytics aggregates
    total_views = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.display_name} (@{self.username})"

    def get_absolute_url(self):
        return f"/{self.username}/"

    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return None


class Appearance(models.Model):
    THEME_CHOICES = [
        ('minimal_light', 'Minimalist Snow (Clean White)'),
        ('midnight_dark', 'Midnight Obsidian (AMOLED Dark)'),
        ('sunset_gradient', 'Sunset Reverie (Vibrant Rose/Violet)'),
        ('emerald_clean', 'Matcha & Sage (Organic Forest)'),
        ('neo_brutalism', 'Neo-Brutalist Pop (Bold Yellow & 3D)'),
        ('cyber_sleek', 'Neon Cyberpunk (Deep Navy & Cyan Glow)'),
        ('velvet_cherry', 'Velvet Cherry (Burgundy & Rose Gold)'),
        ('ocean_aurora', 'Ocean Aurora (Indigo & Teal Wave)'),
        ('paper_editorial', 'Paper & Ink (Warm Editorial Serif)'),
    ]

    BG_TYPE_CHOICES = [
        ('theme', 'Preset Theme Colors'),
        ('color', 'Solid Color'),
        ('gradient', 'Custom Gradient'),
        ('image', 'Custom Background Image'),
    ]

    BUTTON_STYLE_CHOICES = [
        ('glass', 'Frosted Glassmorphism'),
        ('solid', 'Solid Vibrant Fill'),
        ('soft', 'Soft Translucent Tint'),
        ('outline', 'Minimalist Outline'),
        ('hard_3d', 'Hard 3D (Brutalist Offset)'),
        ('glow', 'Ambient Glow Border'),
    ]

    BUTTON_SHAPE_CHOICES = [
        ('rounded', 'Smooth Rounded (14px)'),
        ('pill', 'Full Pill (999px)'),
        ('square', 'Sharp Square (0px)'),
    ]

    CARD_SHADOW_CHOICES = [
        ('none', 'No Shadow (Flat)'),
        ('subtle', 'Subtle Ambient Shadow'),
        ('elevated', 'Elevated Floating Shadow'),
        ('glow', 'Color Glow Halo'),
        ('hard_3d', 'Hard 3D Drop Shadow'),
    ]

    HOVER_EFFECT_CHOICES = [
        ('lift', 'Float Lift (-3px)'),
        ('scale', 'Gentle Zoom (1.02x)'),
        ('glow', 'Glow Border Pulse'),
        ('none', 'Static (No Animation)'),
    ]

    FONT_FAMILY_CHOICES = [
        ('inter', 'Inter (Modern Standard)'),
        ('plus_jakarta_sans', 'Plus Jakarta Sans (SaaS & Tech)'),
        ('outfit', 'Outfit (Clean Geometric)'),
        ('dm_sans', 'DM Sans (Friendly Modern)'),
        ('poppins', 'Poppins (Bold Geometric)'),
        ('space_grotesk', 'Space Grotesk (Tech Futuristic)'),
        ('syne', 'Syne (Avant-Garde Creative)'),
        ('playfair', 'Playfair Display (Luxury Editorial)'),
        ('jetbrains_mono', 'JetBrains Mono (Developer Clean)'),
    ]

    AVATAR_SHAPE_CHOICES = [
        ('circle', 'Circle'),
        ('rounded', 'Rounded Squircle'),
        ('square', 'Sharp Square'),
    ]

    AVATAR_BORDER_CHOICES = [
        ('white', 'White / Light Frame'),
        ('accent', 'Accent Color Ring'),
        ('glow', 'Luminous Glow Halo'),
        ('none', 'No Border'),
    ]

    ALIGNMENT_CHOICES = [
        ('center', 'Centered Profile'),
        ('left', 'Modern Left-Aligned'),
    ]

    SOCIAL_POSITION_CHOICES = [
        ('top', 'Top (Under Bio)'),
        ('bottom', 'Bottom (Above Footer)'),
    ]

    SOCIAL_STYLE_CHOICES = [
        ('colored', 'Official Brand Colors'),
        ('monochrome', 'Monochrome Theme Text'),
        ('glass', 'Frosted Glass Badges'),
    ]

    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='appearance')
    theme = models.CharField(max_length=30, choices=THEME_CHOICES, default='midnight_dark')
    
    # Background options
    bg_type = models.CharField(max_length=20, choices=BG_TYPE_CHOICES, default='theme')
    bg_color = models.CharField(max_length=25, default='#0f172a')
    bg_gradient = models.CharField(
        max_length=200, 
        default='linear-gradient(135deg, #0f172a 0%, #1e1b4b 100%)'
    )
    bg_image = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    bg_overlay_opacity = models.PositiveSmallIntegerField(
        default=30, 
        help_text="Darkness overlay (0 to 90%) for background images so text remains readable"
    )
    bg_blur = models.PositiveSmallIntegerField(
        default=0, 
        help_text="Background blur amount in pixels (0 to 20)"
    )

    # Header & Cover
    banner_image = models.ImageField(upload_to='banners/', blank=True, null=True, help_text="Optional wide profile cover banner")
    profile_alignment = models.CharField(max_length=20, choices=ALIGNMENT_CHOICES, default='center')
    avatar_shape = models.CharField(max_length=20, choices=AVATAR_SHAPE_CHOICES, default='circle')
    avatar_border = models.CharField(max_length=20, choices=AVATAR_BORDER_CHOICES, default='white')

    # Card & Button styling
    button_style = models.CharField(max_length=20, choices=BUTTON_STYLE_CHOICES, default='glass')
    button_shape = models.CharField(max_length=20, choices=BUTTON_SHAPE_CHOICES, default='rounded')
    card_shadow = models.CharField(max_length=20, choices=CARD_SHADOW_CHOICES, default='subtle')
    hover_effect = models.CharField(max_length=20, choices=HOVER_EFFECT_CHOICES, default='lift')
    button_color = models.CharField(max_length=25, default='#3b82f6')
    button_text_color = models.CharField(max_length=25, default='#ffffff')
    accent_color = models.CharField(max_length=25, default='#3b82f6')

    # Typography
    font_family = models.CharField(max_length=30, choices=FONT_FAMILY_CHOICES, default='inter')
    text_color = models.CharField(max_length=25, default='#f8fafc')

    # Social Accounts presentation
    social_position = models.CharField(max_length=10, choices=SOCIAL_POSITION_CHOICES, default='top')
    social_style = models.CharField(max_length=20, choices=SOCIAL_STYLE_CHOICES, default='colored')

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Appearance for @{self.profile.username}"


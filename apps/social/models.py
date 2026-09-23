from django.db import models
from apps.profiles.models import Profile

class SocialAccount(models.Model):
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('tiktok', 'TikTok'),
        ('youtube', 'YouTube'),
        ('twitter', 'X / Twitter'),
        ('linkedin', 'LinkedIn'),
        ('github', 'GitHub'),
        ('threads', 'Threads'),
        ('spotify', 'Spotify'),
        ('facebook', 'Facebook'),
        ('twitch', 'Twitch'),
        ('discord', 'Discord'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='social_accounts')
    platform = models.CharField(max_length=30, choices=PLATFORM_CHOICES)
    url = models.URLField(max_length=300, help_text="Direct link to your social profile")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'platform']
        unique_together = ('profile', 'platform')

    def __str__(self):
        return f"{self.get_platform_display()} - @{self.profile.username}"

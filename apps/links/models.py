from django.db import models
from apps.profiles.models import Profile

class Link(models.Model):
    ICON_CHOICES = [
        ('', 'No Icon (Default)'),
        ('globe', 'Globe / Website'),
        ('video', 'Video / Stream'),
        ('music', 'Music / Audio'),
        ('shopping-bag', 'Store / Merchandise'),
        ('book-open', 'Book / Newsletter'),
        ('podcast', 'Podcast / Audio'),
        ('calendar', 'Calendar / Events'),
        ('sparkles', 'Sparkles / Featured'),
        ('star', 'Star / Highlight'),
        ('heart', 'Heart / Support'),
        ('code', 'Code / Projects'),
        ('file-text', 'Document / Portfolio'),
    ]

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='links')
    title = models.CharField(max_length=120)
    url = models.URLField(max_length=500)
    description = models.CharField(max_length=255, blank=True)
    thumbnail = models.ImageField(upload_to='links/', blank=True, null=True)
    icon = models.CharField(max_length=50, choices=ICON_CHOICES, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, db_index=True)
    click_count = models.PositiveIntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.title} - @{self.profile.username}"

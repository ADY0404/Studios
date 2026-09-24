from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from apps.profiles.models import Profile, Appearance

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if not hasattr(instance, 'profile'):
        # Determine unique username
        base_username = instance.username.lower().strip()
        username = base_username
        counter = 1
        while Profile.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
            
        display_name = f"{instance.first_name} {instance.last_name}".strip() or instance.username
        
        profile = Profile.objects.create(
            user=instance,
            username=username,
            display_name=display_name,
            public_email=instance.email
        )
        Appearance.objects.get_or_create(profile=profile)

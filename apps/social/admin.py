from django.contrib import admin
from django.utils.html import format_html
from apps.social.models import SocialAccount

@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = ('profile', 'platform_badge', 'open_profile_link', 'order', 'is_active')
    list_filter = ('platform', 'is_active')
    search_fields = ('profile__username', 'profile__display_name', 'url')
    list_editable = ('order', 'is_active')
    ordering = ('profile', 'order')

    actions = ['enable_socials', 'disable_socials']

    @admin.display(description="Platform")
    def platform_badge(self, obj):
        return obj.get_platform_display()

    @admin.display(description="Social URL")
    def open_profile_link(self, obj):
        return format_html('<a href="{}" target="_blank" rel="noopener noreferrer" style="font-size: 11px;">{} &nearr;</a>', obj.url, obj.url[:35] + '...' if len(obj.url) > 35 else obj.url)

    @admin.action(description="Enable selected social accounts")
    def enable_socials(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} social account(s) enabled.")

    @admin.action(description="Disable selected social accounts")
    def disable_socials(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} social account(s) disabled.")

from django.contrib import admin
from django.utils.html import format_html
from apps.links.models import Link

@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    list_display = ('title', 'profile', 'open_link', 'order', 'is_active', 'click_count', 'created_at')
    list_filter = ('is_active', 'created_at', 'icon')
    search_fields = ('title', 'url', 'description', 'profile__username', 'profile__display_name')
    ordering = ('profile', 'order')
    list_editable = ('order', 'is_active')
    readonly_fields = ('click_count', 'created_at', 'updated_at')

    fieldsets = (
        ("Link Association", {
            "fields": (("profile", "is_active", "order"),)
        }),
        ("Content & Destination", {
            "fields": ("title", "url", "description")
        }),
        ("Media & Visuals", {
            "fields": (("thumbnail", "icon"),)
        }),
        ("Analytics", {
            "fields": (("click_count", "created_at", "updated_at"),)
        }),
    )

    actions = ['activate_links', 'deactivate_links', 'reset_clicks']

    @admin.display(description="Destination URL")
    def open_link(self, obj):
        return format_html('<a href="{}" target="_blank" rel="noopener noreferrer" style="font-size: 11px;">{} &nearr;</a>', obj.url, obj.url[:35] + '...' if len(obj.url) > 35 else obj.url)

    @admin.action(description="Enable selected links")
    def activate_links(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} link(s) enabled.")

    @admin.action(description="Disable selected links")
    def deactivate_links(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} link(s) disabled.")

    @admin.action(description="Reset click count to 0")
    def reset_clicks(self, request, queryset):
        updated = queryset.update(click_count=0)
        self.message_user(request, f"Click count reset to 0 for {updated} link(s).")

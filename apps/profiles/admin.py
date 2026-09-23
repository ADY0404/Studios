from django.contrib import admin
from django.utils.html import format_html
from apps.profiles.models import Profile, Appearance
from apps.links.models import Link
from apps.social.models import SocialAccount
from apps.bookings.models import Service

# Customize Global Admin Branding
admin.site.site_header = "LinkStudio Command Center"
admin.site.site_title = "LinkStudio Admin"
admin.site.index_title = "Platform Management & Operations"

class AppearanceInline(admin.StackedInline):
    model = Appearance
    can_delete = False
    extra = 0
    verbose_name = 'Appearance Styling'
    verbose_name_plural = 'Appearance Styling'
    fieldsets = (
        ("Theme & Typography", {
            "fields": (("theme", "font_family"), ("text_color", "accent_color"))
        }),
        ("Header & Cover", {
            "fields": (("banner_image", "profile_alignment"), ("avatar_shape", "avatar_border"))
        }),
        ("Background Engine", {
            "fields": (("bg_type", "bg_color"), "bg_gradient", "bg_image", ("bg_overlay_opacity", "bg_blur"))
        }),
        ("Buttons & Cards", {
            "fields": (("button_style", "button_shape"), ("card_shadow", "hover_effect"), ("button_color", "button_text_color"))
        }),
        ("Social Accounts Presentation", {
            "fields": (("social_position", "social_style"),)
        }),
    )

class LinkInline(admin.TabularInline):
    model = Link
    extra = 0
    fields = ('order', 'title', 'url', 'icon', 'is_active', 'click_count')
    readonly_fields = ('click_count',)
    ordering = ('order',)

class SocialAccountInline(admin.TabularInline):
    model = SocialAccount
    extra = 0
    fields = ('platform', 'url', 'order', 'is_active')
    ordering = ('order',)

class ServiceInline(admin.TabularInline):
    model = Service
    extra = 0
    fields = ('title', 'duration_minutes', 'price', 'is_active', 'order')
    ordering = ('order',)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'display_name', 'view_public_page', 'is_verified_badge',
        'public_email', 'is_public', 'total_views', 'created_at'
    )
    list_filter = ('is_verified', 'is_public', 'show_contact_form', 'show_save_contact', 'created_at')
    search_fields = ('username', 'display_name', 'title_tagline', 'public_email', 'user__username', 'user__email')
    readonly_fields = ('total_views', 'created_at', 'updated_at')
    list_editable = ('is_public',)
    inlines = [AppearanceInline, LinkInline, SocialAccountInline, ServiceInline]

    fieldsets = (
        ("Creator Identity & Verification", {
            "fields": (("user", "username"), ("display_name", "title_tagline"), "is_verified")
        }),
        ("Bio & Media", {
            "fields": ("bio", "avatar", ("location", "website"))
        }),
        ("Contact Details", {
            "fields": (("public_email", "phone"),)
        }),
        ("Platform Visibility & Features", {
            "fields": (("is_public", "show_save_contact", "show_contact_form"),)
        }),
        ("Analytics & Metadata", {
            "fields": (("total_views", "created_at", "updated_at"),)
        }),
    )

    actions = ['verify_profiles', 'unverify_profiles', 'make_public', 'make_private', 'reset_views']

    @admin.display(description="Verified", boolean=True)
    def is_verified_badge(self, obj):
        return obj.is_verified

    @admin.display(description="Public Page")
    def view_public_page(self, obj):
        return format_html('<a href="/{}/" target="_blank" class="button" style="padding: 2px 8px; font-size: 11px;">View Bio &rarr;</a>', obj.username)

    @admin.action(description="Mark selected creators as Verified")
    def verify_profiles(self, request, queryset):
        updated = queryset.update(is_verified=True)
        self.message_user(request, f"{updated} creator(s) marked as verified.")

    @admin.action(description="Remove verification from selected creators")
    def unverify_profiles(self, request, queryset):
        updated = queryset.update(is_verified=False)
        self.message_user(request, f"{updated} creator(s) unverified.")

    @admin.action(description="Make selected profiles Public")
    def make_public(self, request, queryset):
        updated = queryset.update(is_public=True)
        self.message_user(request, f"{updated} profile(s) set to Public.")

    @admin.action(description="Hide selected profiles (Private)")
    def make_private(self, request, queryset):
        updated = queryset.update(is_public=False)
        self.message_user(request, f"{updated} profile(s) set to Private.")

    @admin.action(description="Reset View Counter to 0")
    def reset_views(self, request, queryset):
        updated = queryset.update(total_views=0)
        self.message_user(request, f"View counter reset to 0 for {updated} profile(s).")


@admin.register(Appearance)
class AppearanceAdmin(admin.ModelAdmin):
    list_display = ('profile', 'theme', 'bg_type', 'button_style', 'button_shape', 'card_shadow', 'font_family', 'updated_at')
    list_filter = ('theme', 'bg_type', 'button_style', 'button_shape', 'card_shadow', 'font_family')
    search_fields = ('profile__username', 'profile__display_name')
    readonly_fields = ('updated_at',)

    fieldsets = (
        ("Profile Binding", {
            "fields": ("profile",)
        }),
        ("Theme Palette & Typography", {
            "fields": (("theme", "font_family"), ("text_color", "accent_color"))
        }),
        ("Cover Banner & Avatar", {
            "fields": ("banner_image", "profile_alignment", ("avatar_shape", "avatar_border"))
        }),
        ("Background Studio", {
            "fields": (("bg_type", "bg_color"), "bg_gradient", "bg_image", ("bg_overlay_opacity", "bg_blur"))
        }),
        ("Cards, Buttons & Animations", {
            "fields": (("button_style", "button_shape"), ("card_shadow", "hover_effect"), ("button_color", "button_text_color"))
        }),
        ("Social Media Layout", {
            "fields": (("social_position", "social_style"),)
        }),
        ("Timestamps", {
            "fields": ("updated_at",)
        }),
    )

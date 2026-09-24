from django.contrib import admin
from django.utils.html import format_html
from apps.bookings.models import Service, AvailabilityRule, Booking

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('title', 'profile', 'duration_minutes', 'price', 'currency', 'is_active', 'order')
    list_filter = ('is_active', 'currency')
    search_fields = ('title', 'profile__username', 'profile__display_name')
    list_editable = ('price', 'is_active', 'order')
    ordering = ('profile', 'order')

    actions = ['enable_services', 'disable_services']

    @admin.action(description="Activate selected services")
    def enable_services(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} service(s) activated.")

    @admin.action(description="Deactivate selected services")
    def disable_services(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} service(s) deactivated.")


@admin.register(AvailabilityRule)
class AvailabilityRuleAdmin(admin.ModelAdmin):
    list_display = ('profile', 'day_name', 'start_time', 'end_time', 'is_active')
    list_filter = ('day_of_week', 'is_active')
    search_fields = ('profile__username', 'profile__display_name')
    list_editable = ('is_active',)

    @admin.display(description="Day of Week")
    def day_name(self, obj):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[obj.day_of_week] if 0 <= obj.day_of_week < 7 else str(obj.day_of_week)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'visitor_name', 'service', 'profile', 'start_time',
        'status', 'payment_status', 'created_at'
    )
    list_filter = ('status', 'payment_status', 'start_time', 'created_at')
    search_fields = ('visitor_name', 'visitor_email', 'visitor_phone', 'profile__username', 'service__title', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status', 'payment_status')
    ordering = ('-start_time',)

    fieldsets = (
        ("Client Information", {
            "fields": (("visitor_name", "visitor_email", "visitor_phone"),)
        }),
        ("Session Scheduling", {
            "fields": (("profile", "service"), ("start_time", "end_time"))
        }),
        ("Status & Billing", {
            "fields": (("status", "payment_status"),)
        }),
        ("Client Notes", {
            "fields": ("notes",)
        }),
        ("Timestamps", {
            "fields": (("created_at", "updated_at"),)
        }),
    )

    actions = ['confirm_bookings', 'complete_bookings', 'cancel_bookings', 'mark_paid']

    @admin.display(description="Status")
    def status_badge(self, obj):
        colors = {
            'pending': '#f59e0b',
            'confirmed': '#10b981',
            'completed': '#6366f1',
            'cancelled': '#ef4444',
        }
        color = colors.get(obj.status, '#64748b')
        return format_html('<span style="color: white; background: {}; padding: 2px 8px; border-radius: 999px; font-size: 11px; font-weight: bold;">{}</span>', color, obj.get_status_display())

    @admin.display(description="Payment")
    def payment_badge(self, obj):
        colors = {
            'unpaid': '#ef4444',
            'paid': '#10b981',
            'refunded': '#64748b',
        }
        color = colors.get(obj.payment_status, '#64748b')
        return format_html('<span style="color: white; background: {}; padding: 2px 8px; border-radius: 999px; font-size: 11px; font-weight: bold;">{}</span>', color, obj.get_payment_status_display())

    @admin.action(description="Mark selected bookings as Confirmed")
    def confirm_bookings(self, request, queryset):
        from apps.bookings.emails import send_booking_status_update_email
        count = 0
        for booking in queryset:
            booking.status = 'confirmed'
            booking.save(update_fields=['status', 'updated_at'])
            send_booking_status_update_email(booking)
            count += 1
        self.message_user(request, f"{count} booking(s) marked as confirmed and notification emails sent.")

    @admin.action(description="Mark selected bookings as Completed")
    def complete_bookings(self, request, queryset):
        updated = queryset.update(status='completed')
        self.message_user(request, f"{updated} booking(s) marked as completed.")

    @admin.action(description="Cancel selected bookings")
    def cancel_bookings(self, request, queryset):
        from apps.bookings.emails import send_booking_status_update_email
        count = 0
        for booking in queryset:
            booking.status = 'cancelled'
            booking.save(update_fields=['status', 'updated_at'])
            send_booking_status_update_email(booking)
            count += 1
        self.message_user(request, f"{count} booking(s) cancelled and notification emails sent.")

    @admin.action(description="Mark selected bookings as Paid")
    def mark_paid(self, request, queryset):
        updated = queryset.update(payment_status='paid')
        self.message_user(request, f"{updated} booking(s) marked as paid.")

    def save_model(self, request, obj, form, change):
        old_status = None
        if change and 'status' in form.changed_data:
            old_booking = Booking.objects.filter(pk=obj.pk).first()
            if old_booking:
                old_status = old_booking.status
        super().save_model(request, obj, form, change)
        if old_status and old_status != obj.status:
            from apps.bookings.emails import send_booking_status_update_email
            send_booking_status_update_email(obj)

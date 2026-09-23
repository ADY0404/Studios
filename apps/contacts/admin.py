import csv
from django.contrib import admin
from django.http import HttpResponse
from apps.contacts.models import ContactSubmission

@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'profile', 'message_snippet', 'created_at')
    list_filter = ('created_at', 'profile')
    search_fields = ('name', 'email', 'phone', 'message', 'profile__username', 'profile__display_name')
    readonly_fields = ('name', 'email', 'phone', 'message', 'profile', 'created_at')
    ordering = ('-created_at',)

    actions = ['export_as_csv']

    @admin.display(description="Inquiry Message")
    def message_snippet(self, obj):
        return obj.message[:60] + ('...' if len(obj.message) > 60 else '')

    @admin.action(description="Export selected inquiries to CSV")
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="linkstudio_inquiries.csv"'
        writer = csv.writer(response)
        writer.writerow(['Creator', 'Client Name', 'Email', 'Phone', 'Message', 'Date Submitted'])
        for item in queryset:
            writer.writerow([
                item.profile.username,
                item.name,
                item.email,
                item.phone,
                item.message,
                item.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        return response

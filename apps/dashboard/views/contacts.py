import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST

from apps.contacts.models import ContactSubmission


@login_required
def contacts_manager(request):
    profile = request.user.profile
    query = request.GET.get('q', '').strip()
    
    contacts_qs = profile.contacts.all().order_by('-created_at')
    if query:
        contacts_qs = contacts_qs.filter(name__icontains=query) | contacts_qs.filter(email__icontains=query)

    paginator = Paginator(contacts_qs, 25)
    page_number = request.GET.get('page')
    contacts = paginator.get_page(page_number)

    return render(request, 'dashboard/contacts.html', {
        'profile': profile,
        'contacts': contacts,
        'query': query
    })


# SECURITY: Mitigate CSV injection (formula injection) per OWASP recommendations
def sanitize_csv_field(value):
    if value is None:
        return ""
    str_val = str(value)
    if str_val and str_val[0] in ('=', '+', '-', '@', '\t', '\r'):
        return f"'{str_val}"
    return str_val


@login_required
def export_contacts_csv(request):
    profile = request.user.profile
    contacts = profile.contacts.all().order_by('-created_at')
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{profile.username}_contacts.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Phone', 'Message', 'Date Submitted'])
    
    for c in contacts:
        writer.writerow([
            sanitize_csv_field(c.name),
            sanitize_csv_field(c.email),
            sanitize_csv_field(c.phone),
            sanitize_csv_field(c.message),
            c.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    return response


@login_required
@require_POST
def delete_contact(request, contact_id):
    profile = request.user.profile
    contact = get_object_or_404(ContactSubmission, id=contact_id, profile=profile)
    name = contact.name
    contact.delete()
    messages.success(request, f"Contact record for '{name}' was deleted.")
    return redirect('dashboard:contacts')


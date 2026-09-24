from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.links.models import Link
from apps.links.forms import LinkForm


@login_required
def links_manager(request):
    profile = request.user.profile
    links = profile.links.all().order_by('order', '-created_at')
    
    if request.method == 'POST':
        form = LinkForm(request.POST, request.FILES)
        if form.is_valid():
            new_link = form.save(commit=False)
            new_link.profile = profile
            # Put new link at the end of the order
            max_order = links.last().order if links.exists() else 0
            new_link.order = max_order + 1
            new_link.save()
            messages.success(request, f"Link '{new_link.title}' created successfully!")
            return redirect('dashboard:links')
    else:
        form = LinkForm()

    return render(request, 'dashboard/links.html', {
        'profile': profile,
        'links': links,
        'form': form
    })


@login_required
def edit_link(request, link_id):
    profile = request.user.profile
    link = get_object_or_404(Link, id=link_id, profile=profile)
    
    if request.method == 'POST':
        form = LinkForm(request.POST, request.FILES, instance=link)
        if form.is_valid():
            form.save()
            messages.success(request, f"Link '{link.title}' updated!")
            return redirect('dashboard:links')
    else:
        form = LinkForm(instance=link)

    return render(request, 'dashboard/link_edit.html', {
        'profile': profile,
        'link': link,
        'form': form
    })


@login_required
@require_POST
def toggle_link(request, link_id):
    profile = request.user.profile
    link = get_object_or_404(Link, id=link_id, profile=profile)
    link.is_active = not link.is_active
    link.save(update_fields=['is_active'])
    status_str = "enabled" if link.is_active else "disabled"
    messages.info(request, f"Link '{link.title}' {status_str}.")
    return redirect('dashboard:links')


@login_required
@require_POST
def delete_link(request, link_id):
    profile = request.user.profile
    link = get_object_or_404(Link, id=link_id, profile=profile)
    title = link.title
    link.delete()
    messages.success(request, f"Link '{title}' was deleted.")
    return redirect('dashboard:links')


@login_required
@require_POST
def move_link_up(request, link_id):
    profile = request.user.profile
    link = get_object_or_404(Link, id=link_id, profile=profile)
    prev_link = profile.links.filter(order__lt=link.order).order_by('-order').first()
    if prev_link:
        link.order, prev_link.order = prev_link.order, link.order
        Link.objects.bulk_update([link, prev_link], ['order'])
    return redirect('dashboard:links')


@login_required
@require_POST
def move_link_down(request, link_id):
    profile = request.user.profile
    link = get_object_or_404(Link, id=link_id, profile=profile)
    next_link = profile.links.filter(order__gt=link.order).order_by('order').first()
    if next_link:
        link.order, next_link.order = next_link.order, link.order
        Link.objects.bulk_update([link, next_link], ['order'])
    return redirect('dashboard:links')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reorder_links_api(request):
    """
    Accepts JSON payload: { 'order': [id1, id2, id3, ...] }
    and updates the position index cleanly without duplicates.
    """
    profile = request.user.profile
    order_ids = request.data.get('order', [])
    
    if not isinstance(order_ids, list):
        return Response({'error': 'Invalid format. Array of IDs expected.'}, status=400)

    # Fetch user's links
    user_links = {link.id: link for link in profile.links.filter(id__in=order_ids)}
    
    updates = []
    for index, link_id in enumerate(order_ids):
        try:
            link_id_int = int(link_id)
        except (ValueError, TypeError):
            continue
        if link_id_int in user_links:
            link = user_links[link_id_int]
            link.order = index
            updates.append(link)

    if updates:
        Link.objects.bulk_update(updates, ['order'])

    return Response({'status': 'success', 'updated_count': len(updates)})


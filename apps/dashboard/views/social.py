from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST

from apps.social.models import SocialAccount
from apps.social.forms import SocialAccountForm


@login_required
def social_manager(request):
    profile = request.user.profile
    socials = profile.social_accounts.all().order_by('order', 'platform')

    if request.method == 'POST':
        form = SocialAccountForm(request.POST)
        if form.is_valid():
            platform = form.cleaned_data['platform']
            # Update existing or create new
            account, created = SocialAccount.objects.update_or_create(
                profile=profile,
                platform=platform,
                defaults={
                    'url': form.cleaned_data['url'],
                    'is_active': form.cleaned_data['is_active']
                }
            )
            msg = f"{account.get_platform_display()} added!" if created else f"{account.get_platform_display()} updated!"
            messages.success(request, msg)
            return redirect('dashboard:social')
    else:
        form = SocialAccountForm()

    return render(request, 'dashboard/social.html', {
        'profile': profile,
        'socials': socials,
        'form': form
    })


@login_required
@require_POST
def delete_social(request, social_id):
    profile = request.user.profile
    account = get_object_or_404(SocialAccount, id=social_id, profile=profile)
    name = account.get_platform_display()
    account.delete()
    messages.success(request, f"{name} profile removed.")
    return redirect('dashboard:social')


@login_required
@require_POST
def toggle_social(request, social_id):
    profile = request.user.profile
    account = get_object_or_404(SocialAccount, id=social_id, profile=profile)
    account.is_active = not account.is_active
    account.save(update_fields=['is_active'])
    status_str = "enabled" if account.is_active else "disabled"
    messages.info(request, f"{account.get_platform_display()} {status_str}.")
    return redirect('dashboard:social')


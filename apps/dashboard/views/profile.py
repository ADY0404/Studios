from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.profiles.forms import ProfileForm


@login_required
def profile_details(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Creator profile updated successfully!")
            return redirect('dashboard:profile')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'dashboard/profile.html', {
        'profile': profile,
        'form': form
    })


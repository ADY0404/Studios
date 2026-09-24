from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from apps.profiles.models import Appearance
from apps.profiles.forms import AppearanceForm


@login_required
def appearance_studio(request):
    profile = request.user.profile
    appearance, _ = Appearance.objects.get_or_create(profile=profile)

    if request.method == 'POST':
        form = AppearanceForm(request.POST, request.FILES, instance=appearance)
        if form.is_valid():
            app_obj = form.save(commit=False)

            # Determine bg_type based on file upload / clear actions
            new_image_uploaded = 'bg_image' in request.FILES and request.FILES['bg_image']
            image_cleared = request.POST.get('bg_image-clear') or request.POST.get('clear_bg_image') == 'true'

            if new_image_uploaded:
                # New image uploaded — force bg_type to 'image'
                app_obj.bg_type = 'image'
            elif image_cleared:
                # Image cleared — revert bg_type to the selected type (gradient/color)
                # Manually delete existing image if still set on the instance
                if appearance.bg_image:
                    appearance.bg_image.delete(save=False)
                app_obj.bg_image = None
                if app_obj.bg_type == 'image':
                    app_obj.bg_type = 'gradient'

            app_obj.save()
            messages.success(request, 'Appearance saved! Your profile is updated.')
            return redirect('dashboard:appearance')
        else:
            for field, errs in form.errors.items():
                for err in errs:
                    field_name = 'General' if field == '__all__' else field.replace('_', ' ').capitalize()
                    messages.error(request, f"{field_name}: {err}")
    else:
        form = AppearanceForm(instance=appearance)

    return render(request, 'dashboard/appearance.html', {
        'profile': profile,
        'appearance': appearance,
        'form': form
    })


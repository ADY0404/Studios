import os
from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage


class Command(BaseCommand):
    help = "Upload all existing local media files (photos, videos) from MEDIA_ROOT to Cloudinary."

    def handle(self, *args, **options):
        if not getattr(settings, 'USE_CLOUDINARY', False):
            self.stderr.write(
                self.style.ERROR(
                    "Cloudinary is not enabled. Please define CLOUDINARY_CLOUD_NAME, "
                    "CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET in your .env file first."
                )
            )
            return

        media_root = settings.MEDIA_ROOT
        if not os.path.exists(media_root):
            self.stdout.write(self.style.WARNING(f"Media directory does not exist: {media_root}"))
            return

        uploaded_count = 0
        skipped_count = 0
        error_count = 0

        self.stdout.write(self.style.NOTICE(f"Scanning media directory: {media_root} ..."))

        for root, dirs, files in os.walk(media_root):
            for filename in files:
                if filename.startswith('.') or filename == '.gitkeep':
                    continue

                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, media_root).replace('\\', '/')

                try:
                    if default_storage.exists(rel_path):
                        self.stdout.write(f"  [SKIP] Already on Cloudinary: {rel_path}")
                        skipped_count += 1
                        continue

                    self.stdout.write(f"  [UPLOADING] {rel_path} ...", ending="")
                    with open(full_path, 'rb') as f:
                        saved_name = default_storage.save(rel_path, f)
                    self.stdout.write(self.style.SUCCESS(f" DONE -> {saved_name}"))
                    uploaded_count += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f" FAILED: {e}"))
                    error_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nFinished! Uploaded: {uploaded_count}, Skipped: {skipped_count}, Errors: {error_count}"
            )
        )


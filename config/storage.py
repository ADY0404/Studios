import os
from cloudinary_storage.storage import MediaCloudinaryStorage


class AdaptiveMediaCloudinaryStorage(MediaCloudinaryStorage):
    """
    Custom Cloudinary storage that automatically detects media type
    (image, video, raw) from file extensions so creators can upload
    both photos and videos seamlessly.
    """
    VIDEO_EXTENSIONS = (
        '.mp4', '.mov', '.avi', '.wmv', '.flv', '.mkv', '.webm', '.m4v', '.ogv'
    )
    RAW_EXTENSIONS = (
        '.pdf', '.zip', '.tar', '.gz', '.doc', '.docx', '.csv', '.xlsx'
    )

    def _get_resource_type(self, name):
        ext = os.path.splitext(name)[1].lower()
        if ext in self.VIDEO_EXTENSIONS:
            return 'video'
        elif ext in self.RAW_EXTENSIONS:
            return 'raw'
        return 'image'


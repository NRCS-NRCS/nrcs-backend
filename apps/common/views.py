import datetime
import os

from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import generic
from django.views.decorators.clickjacking import xframe_options_sameorigin
from django.views.decorators.csrf import csrf_exempt
from mdeditor.configs import MDConfig

from utils.common import MAX_MDEDITOR_IMAGE_FILE_SIZE

MDEDITOR_CONFIGS = MDConfig("default")


# editor.md submits the upload through a hidden same-origin <iframe> and reads the
# JSON response out of it. The site-wide ``X_FRAME_OPTIONS = "DENY"`` would block
# the browser from rendering that response in the iframe, so the editor could never
# read the uploaded image URL. ``xframe_options_sameorigin`` relaxes the header to
# SAMEORIGIN for this response only, leaving DENY in place everywhere else.
@method_decorator(csrf_exempt, name="dispatch")
@method_decorator(xframe_options_sameorigin, name="dispatch")
class MDEditorImageUploadView(generic.View):
    """Drop-in replacement for ``mdeditor.views.UploadView``.

    The bundled mdeditor upload view writes the file to the local filesystem with
    a raw ``open(MEDIA_ROOT/...)`` and returns a ``MEDIA_URL/...`` path, bypassing
    Django's configured storage backend. On S3-backed deployments the file never
    reaches the bucket and the returned URL does not resolve, so image upload
    appears broken.

    This view saves the image through ``default_storage`` (S3 or filesystem) and
    returns ``default_storage.url(...)`` so it works in every environment. The
    JSON response contract matches mdeditor's so the editor.md frontend is happy.
    """

    def post(self, request, *args, **kwargs):
        upload_image = request.FILES.get("editormd-image-file")
        if not upload_image:
            return JsonResponse({"success": 0, "message": "No image was received.", "url": ""})

        allowed_formats = MDEDITOR_CONFIGS["upload_image_formats"]
        stem, _, extension = upload_image.name.rpartition(".")
        extension = extension.lower()
        if not stem or extension not in allowed_formats:
            return JsonResponse(
                {
                    "success": 0,
                    "message": "Unsupported image format. Allowed formats: %s" % ", ".join(allowed_formats),
                    "url": "",
                },
            )

        max_size_bytes = MAX_MDEDITOR_IMAGE_FILE_SIZE * 1024 * 1024
        if upload_image.size > max_size_bytes:
            return JsonResponse(
                {
                    "success": 0,
                    "message": "Image is too large. Max size must be less than %s MB." % MAX_MDEDITOR_IMAGE_FILE_SIZE,
                    "url": "",
                },
            )

        file_name = "%s_%s.%s" % (
            stem,
            datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"),
            extension,
        )
        saved_path = default_storage.save(
            os.path.join(MDEDITOR_CONFIGS["image_folder"], file_name),
            upload_image,
        )
        return JsonResponse({"success": 1, "message": "Upload success.", "url": default_storage.url(saved_path)})

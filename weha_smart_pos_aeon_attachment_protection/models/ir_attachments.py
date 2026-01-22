import base64
import mimetypes
import os

try:
    import magic  # pip install python-magic
except ImportError:
    magic = None

from odoo import models, api, _, fields
from odoo.exceptions import ValidationError


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("datas") and vals.get("datas_fname"):
                filename = vals["datas_fname"]
                ext = os.path.splitext(filename)[1].lower()
                if ext not in [".jpg", ".png", ".pdf"]:
                    raise ValidationError(_("Only JPG, PNG, PDF files allowed. You uploaded: %s") % ext)
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("datas") or vals.get("datas_fname"):
            self._check_file(vals)
        return super().write(vals)

    # def _get_config(self):
    #     """Load settings from system parameters"""
    #     ir_config = self.env['ir.config_parameter'].sudo()

    #     # Extensions (comma separated)
    #     exts = ir_config.get_param("attachment_protection.allowed_extensions", ".jpg,.jpeg,.png,.pdf")
    #     allowed_extensions = [x.strip().lower() for x in exts.split(",") if x]

    #     # MIME types (comma separated)
    #     mimes = ir_config.get_param("attachment_protection.allowed_mimetypes", "image/jpeg,image/png,application/pdf")
    #     allowed_mimes = [x.strip().lower() for x in mimes.split(",") if x]

    #     # Max size
    #     max_size = ir_config.get_param("attachment_protection.max_file_size_mb", "5")
    #     try:
    #         max_size = int(max_size)
    #     except ValueError:
    #         max_size = 5

    #     return allowed_extensions, allowed_mimes, max_size

    # def _check_file(self, vals):
    #     """Validate file before saving"""
    #     if not vals.get("datas") or not vals.get("datas_fname"):
    #         return

    #     allowed_extensions, allowed_mimes, max_size = self._get_config()

    #     filename = vals["datas_fname"]
    #     ext = os.path.splitext(filename)[1].lower()

    #     # Decode file content
    #     file_data = base64.b64decode(vals["datas"])
    #     file_size_mb = len(file_data) / (1024 * 1024)

    #     # Extension check
    #     if ext not in allowed_extensions:
    #         raise ValidationError(
    #             _("File extension '%s' not allowed. Allowed: %s") %
    #             (ext, ", ".join(allowed_extensions))
    #         )

    #     # MIME check (fallback to mimetypes if python-magic not available)
    #     if magic:
    #         mime_type = magic.from_buffer(file_data, mime=True)
    #     else:
    #         mime_type, _ = mimetypes.guess_type(filename)

    #     if not mime_type or mime_type.lower() not in allowed_mimes:
    #         raise ValidationError(
    #             _("File type not allowed: %s. Allowed: %s") %
    #             (mime_type or "Unknown", ", ".join(allowed_mimes))
    #         )

    #     # Size check
    #     if file_size_mb > max_size:
    #         raise ValidationError(
    #             _("File too large (%.2f MB). Maximum allowed is %d MB.") %
    #             (file_size_mb, max_size)
    #         )

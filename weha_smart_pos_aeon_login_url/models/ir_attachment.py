from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import mimetypes


import logging
_logger = logging.getLogger(__name__)


ALLOWED_MIME_TYPES = [
    'application/pdf',
    'image/jpeg',
    'image/png',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # .xlsx
    'text/plain', 
    'text/javascript', 
    'text/css',
    # Add other allowed MIME types here
]

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'
    
    @api.model
    def create(self, vals):
        _logger.info("Creating attachment with vals: %s", vals.get('name', ''))
        # if vals.get('datas'):
        mimetype = mimetypes.guess_type(vals.get('name', ''))[0]
        _logger.info(mimetype)
        if mimetype and mimetype not in ALLOWED_MIME_TYPES:
            raise ValidationError(_('File type %s is not allowed.') % mimetype)
        return super(IrAttachment, self).create(vals)
    
    
    # @api.constrains('datas', 'name', 'mimetype')
    # def _check_file_type(self):
    #     allowed_types = ['application/pdf', 'image/jpeg', 'image/png']
    #     for record in self:
    #         mime_type = record.mimetype
    #         # Fallback to mimetypes if not set
    #         if not mime_type and record.name:
    #             mime_type, _ = mimetypes.guess_type(record.name)
    #         if mime_type and mime_type not in ALLOWED_MIME_TYPES:
    #             raise ValidationError(_('File type %s is not allowed.') % mime_type)

                # raise ValidationError('Invalid file type. Only PDF and images are allowed.')

# -*- coding: utf-8 -*-
###############################################################################
#    License, author and contributors information in:                         #
#    __manifest__.py file at the root folder of this module.                  #
###############################################################################

import base64
import functools
import io
import json
import logging
import os
import unicodedata

try:
    from werkzeug.utils import send_file
except ImportError:
    from odoo.tools._vendor.send_file import send_file

import odoo
import odoo.modules.registry
from odoo import http, _
from odoo.exceptions import AccessError, UserError
from odoo.http import request, Response
from odoo.modules import get_resource_path
from odoo.tools import file_open, file_path, replace_exceptions
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools.image import image_guess_size_from_field_name


_logger = logging.getLogger(__name__)


class DisplayController(http.Controller):

    @http.route(['/store/imagelist/<code>'], type='http', auth="public", cors="*")
    def image_list(self, code):    
        res_branch_id = request.env['res.branch'].sudo().search([('code','=',code)], limit=1)
        if res_branch_id:
            return json.dumps(res_branch_id.image_ids.ids)
        return json.dumps([])
        

    @http.route(['/store/image/<int:id>'], type='http', auth="public")
    # pylint: disable=redefined-builtin,invalid-name
    def content_image(self, xmlid=None, model='res.branch.display.image', id=None, field='filebin',
                      filename_field='name', filename=None, mimetype=None, unique=False,
                      download=False, width=0, height=0, crop=False, access_token=None,
                      nocache=False):
        try:
            record = request.env['ir.binary'].sudo()._find_record(xmlid, model, id and int(id), access_token)
            stream = request.env['ir.binary'].sudo()._get_image_stream_from(
                record, field, filename=filename, filename_field=filename_field,
                mimetype=mimetype, width=int(width), height=int(height), crop=crop,
            )
        except UserError as exc:
            if download:
                raise request.not_found() from exc
            # Use the ratio of the requested field_name instead of "raw"
            if (int(width), int(height)) == (0, 0):
                width, height = image_guess_size_from_field_name(field)
            record = request.env.ref('web.image_placeholder').sudo()
            stream = request.env['ir.binary'].sudo()._get_image_stream_from(
                record, 'raw', width=int(width), height=int(height), crop=crop,
            )

        send_file_kwargs = {'as_attachment': download}
        if unique:
            send_file_kwargs['immutable'] = True
            send_file_kwargs['max_age'] = http.STATIC_CACHE_LONG
        if nocache:
            send_file_kwargs['max_age'] = None

        return stream.get_response(**send_file_kwargs)

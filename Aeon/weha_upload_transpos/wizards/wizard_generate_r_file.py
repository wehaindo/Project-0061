from odoo import models, fields, api, _ 

import logging
_logger = logging.getLogger(__name__)


AVAILABLE_TIMES = [
    ("1", "08:00:00 - 08:30:00"),
    ("2", "08:30:00 - 09:00:00"),
    ("3", "09:00:00 - 09:30:00"),
    ("4", "09:30:00 - 10:00:00"),
    ("5", "10:00:00 - 10:30:00"),
    ("6", "10:30:00 - 11:00:00"),
    ("7", "11:00:00 - 11:30:00"),
    ("8", "11:30:00 - 12:00:00"),
    ("9", "12:00:00 - 12:30:00"),
    ("10", "12:30:00 - 13:00:00"),
    ("11", "13:00:00 - 13:30:00"),
    ("12", "13:30:00 - 14:00:00"),
    ("13", "14:00:00 - 14:30:00"),
    ("14", "14:30:00 - 15:00:00"),
    ("15", "15:00:00 - 15:30:00"),
    ("16", "15:30:00 - 16:00:00"),
    ("17", "16:00:00 - 16:30:00"),
    ("18", "16:30:00 - 17:00:00"),
    ("19", "17:00:00 - 17:30:00"),
    ("20", "17:30:00 - 18:00:00"),
    ("21", "18:00:00 - 18:30:00"),
    ("22", "18:30:00 - 19:00:00"),
    ("23", "19:00:00 - 19:30:00"),
    ("24", "19:30:00 - 20:00:00"),
    ("25", "20:00:00 - 20:30:00"),
    ("26", "20:30:00 - 21:00:00"),
    ("27", "21:00:00 - 21:30:00"),
    ("28", "21:30:00 - 22:00:00"),
    ("29", "22:00:00 - 22:30:00"),
    ("30", "22:30:00 - 23:00:00") 
]

class WizardGenRFile(models.TransientModel):
    _name = 'wizard.gen.r.file'
    _description = 'Wizard Generate R File'

    def trans_generate_r_file(self):
        if self.duration == "1":
            str_date = self.name.strftime('%Y-%m-%d') + ' 08:30:00'
        elif self.duration == "2":
            str_date = self.name.strftime('%Y-%m-%d') + ' 09:00:00'
        elif self.duration == "3":
            str_date = self.name.strftime('%Y-%m-%d') + ' 09:30:00'
        elif self.duration == "4":
            str_date = self.name.strftime('%Y-%m-%d') + ' 10:00:00'
        elif self.duration == "5":
            str_date = self.name.strftime('%Y-%m-%d') + ' 10:30:00'
        elif self.duration == "6":
            str_date = self.name.strftime('%Y-%m-%d') + ' 11:00:00'
        elif self.duration == "7":
            str_date = self.name.strftime('%Y-%m-%d') + ' 11:30:00'
        elif self.duration == "8":
            str_date = self.name.strftime('%Y-%m-%d') + ' 12:00:00'
        elif self.duration == "9":
            str_date = self.name.strftime('%Y-%m-%d') + ' 12:30:00'
        elif self.duration == "10":
            str_date = self.name.strftime('%Y-%m-%d') + ' 13:00:00'
        elif self.duration == "11":
            str_date = self.name.strftime('%Y-%m-%d') + ' 13:30:00'
        elif self.duration == "12":
            str_date = self.name.strftime('%Y-%m-%d') + ' 14:00:00'
        elif self.duration == "13":
            str_date = self.name.strftime('%Y-%m-%d') + ' 14:30:00'
        elif self.duration == "14":
            str_date = self.name.strftime('%Y-%m-%d') + ' 15:00:00'
        elif self.duration == "15":
            str_date = self.name.strftime('%Y-%m-%d') + ' 15:30:00'
        elif self.duration == "16":
            str_date = self.name.strftime('%Y-%m-%d') + ' 16:00:00'
        elif self.duration == "17":
            str_date = self.name.strftime('%Y-%m-%d') + ' 16:30:00'
        elif self.duration == "18":
            str_date = self.name.strftime('%Y-%m-%d') + ' 17:00:00'
        elif self.duration == "19":
            str_date = self.name.strftime('%Y-%m-%d') + ' 17:30:00'
        elif self.duration == "20":
            str_date = self.name.strftime('%Y-%m-%d') + ' 18:00:00'
        elif self.duration == "21":
            str_date = self.name.strftime('%Y-%m-%d') + ' 18:30:00'
        elif self.duration == "22":
            str_date = self.name.strftime('%Y-%m-%d') + ' 19:00:00'
        elif self.duration == "23":
            str_date = self.name.strftime('%Y-%m-%d') + ' 19:30:00'
        elif self.duration == "24":
            str_date = self.name.strftime('%Y-%m-%d') + ' 20:00:00'
        elif self.duration == "25":
            str_date = self.name.strftime('%Y-%m-%d') + ' 20:30:00'
        elif self.duration == "26":
            str_date = self.name.strftime('%Y-%m-%d') + ' 21:00:00'
        elif self.duration == "27":
            str_date = self.name.strftime('%Y-%m-%d') + ' 21:30:00'
        elif self.duration == "28":
            str_date = self.name.strftime('%Y-%m-%d') + ' 22:00:00'
        elif self.duration == "29":
            str_date = self.name.strftime('%Y-%m-%d') + ' 22:30:00'
        elif self.duration == "30":
            str_date = self.name.strftime('%Y-%m-%d') + ' 23:00:00'

        _logger.info(str_date)
        self.env['pos.trans.code'].get_transpos(assign_date_time=str_date)
            
    name = fields.Date('Date', required=True)
    duration = fields.Selection(AVAILABLE_TIMES,'Duration', required=True)
    is_copy = fields.Boolean("Create Copy to Profit Com", default=False)
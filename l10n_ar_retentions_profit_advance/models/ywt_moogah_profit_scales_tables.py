# -*- coding: utf-8 -*

from odoo import api, fields, models, _

class YWTMoogahProfitScalesTablesHeader(models.Model):
    _name = "ywt.moogah.profit.scales.tables.header"
    _description = "Moogah Profit Scales Tables Header"

    name = fields.Char(string="Nombre Escala",required=True)
    line_ids = fields.One2many('ywt.moogah.profit.scales.tables','table_id',string="Escala")


class YWTMoogahProfitScalesTables(models.Model):
    _name = "ywt.moogah.profit.scales.tables"
    _description = "Moogah Profit Scales Tables"
    _rec_name = ''

    from_dollar = fields.Float(string="Desde $", translate=False)
    to_dollar = fields.Float(string="Hasta $", translate=False)
    plus_dollar = fields.Float(string="+ $", translate=False)
    plus_percentage = fields.Float(string="Mas %", translate=False)
    value_over_dollar = fields.Float(string="Valor Adic. $", translate=False)
    table_id = fields.Many2one('ywt.moogah.profit.scales.tables.header')

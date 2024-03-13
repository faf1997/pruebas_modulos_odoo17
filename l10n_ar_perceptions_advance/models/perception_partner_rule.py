# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PerceptionPartnerRule(models.Model):
    _name = 'perception.partner.rule'
    _description = 'Reglas de percepciones de terceros'

    @api.constrains('percentage', 'perception_id')
    def _check_percentage(self):
        if any(partner_rule.percentage < 0 or partner_rule.percentage > 100 for partner_rule in self):
            raise ValidationError("El porcentaje debe estar entre 0 y 100")

    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Cliente',
        ondelete="cascade",
    )

    perception_id = fields.Many2one(
        comodel_name='perception.perception',
        string='Percepcion',
        required=True,
        domain=lambda l: [('type_tax_use','=','sale'), ('company_id', '=', l.env.company.id)],
    )

    percentage = fields.Float(
        string='Porcentaje',
        required=True,
        digits=(16, 5)
    )

    type = fields.Selection(
        selection=[
            ('vat', 'IVA'),
            ('gross_income', 'Ingresos Brutos'),
            ('profit', 'Ganancias'),
            ('other', 'Otro'),
        ],
        string="Tipo",
        related='perception_id.type',
        readonly=True,
    )

    state_id = fields.Many2one(
        'res.country.state',
        string="Provincia",
        related='perception_id.state_id',
        readonly=True,
    )

    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Empresa',
        readonly=True,
        change_default=True,
        default=lambda self: self.env['res.company']._company_default_get('perception.partner.rule'),
    )

    date_from = fields.Date(
        'Fecha desde'
    )

    date_to = fields.Date(
        'Fecha hasta'
    )

    exception_date = fields.Date(
        'Excepción hasta'
    )

    def is_excepted(self, date):
        return self.exception_date and self.exception_date >= date

    _sql_constraints = [
        ("rule_uniq", "unique(perception_id,partner_id,company_id)", "Ya existe una regla con esa percepción")
    ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

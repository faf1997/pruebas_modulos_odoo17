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


class ResCompanyPerception(models.Model):

    _name = 'res.company.perception'

    @api.constrains('company_id', 'perception_id')
    def _check_repeat(self):
        for company_perception in self:
            rules = self.search([
                ('company_id', '=', company_perception.company_id.id),
                ('perception_id', '=', company_perception.perception_id.id),
                ('id', '!=', company_perception.id)
            ])
            if rules:
                raise ValidationError("Existe mas de una regla con percepcion {}.".format(
                    company_perception.perception_id.name)
                )

    perception_id = fields.Many2one(
        comodel_name='perception.perception',
        string='Percepcion',
        domain="[('type_tax_use','=','sale')]",
        required=True,
        check_company=True
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Empresa',
        readonly=True,
        change_default=True,
        default=lambda self: self.env.company,
    )

    state_id = fields.Many2one(
        comodel_name='res.country.state',
        string="Provincia",
        related='perception_id.state_id',
        readonly=True,
    )

    type = fields.Selection(
        selection=[
            ('vat', 'IVA'),
            ('gross_income', 'Ingresos Brutos'),
            ('profit', 'Ganancias'),
            ('other', 'Otro')
        ],
        string="Tipo",
        related='perception_id.type',
        readonly=True,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

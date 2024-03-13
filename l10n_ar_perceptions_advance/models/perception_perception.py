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


class PerceptionPerception(models.Model):

    _inherit = 'perception.perception'

    @api.constrains('perception_rule_ids')
    def _check_rules(self):
        for perception in self:
            if perception.type_tax_use == 'sale' and perception.type == 'gross_income' and len(
                    perception.perception_rule_ids) > 1:
                raise ValidationError("Para este tipo de percepción solo debe existir una regla")

    perception_rule_ids = fields.One2many(
        comodel_name='perception.perception.rule',
        inverse_name='perception_id',
        string="Reglas de percepcion"
    )

    @api.onchange('type_tax_use')
    def onchange_type_tax_use(self):
        self.perception_rule_ids = [(2, rule.id) for rule in self.perception_rule_ids]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

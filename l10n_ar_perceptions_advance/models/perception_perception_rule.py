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


class PerceptionPerceptionRule(models.Model):

    _name = 'perception.perception.rule'

    @api.constrains('not_applicable_minimum')
    def _check_not_applicable_minimum(self):
        if any(perception_rule.not_applicable_minimum < 0 for perception_rule in self):
            raise ValidationError("El minimo no imponible no puede ser negativo.")

    @api.constrains('minimum_tax')
    def _check_minimum_tax(self):
        if any(perception_rule.minimum_tax < 0 for perception_rule in self):
            raise ValidationError("El impuesto minimo no puede ser negativo.")

    @api.constrains('percentage', 'perception_id')
    def _check_percentage(self):
        if any(perception_rule.percentage < 0 or perception_rule.percentage > 100 for perception_rule in self):
            raise ValidationError("El porcentaje debe estar entre 0 y 100")

    perception_id = fields.Many2one(
        comodel_name='perception.perception',
        string="Percepcion",
        ondelete='cascade',
    )

    not_applicable_minimum = fields.Float(
        string='Minimo no imponible',
        required=True,
    )

    minimum_tax = fields.Float(
        string='Impuesto minimo',
        required=True,
    )

    percentage = fields.Float(
        string='Porcentaje',
        required=True,
        digits=(16, 5)
    )

    exclude_minimum = fields.Boolean(
        string='Excluir minimo',
        default=False,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

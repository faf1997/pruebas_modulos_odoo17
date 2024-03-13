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
from odoo.exceptions import Warning


class RetentionRetentionRule(models.Model):
    _name = 'retention.retention.rule'
    _description = 'Regla de retencion'

    @api.constrains('retention_id', 'activity_id')
    def _check_activity(self):
        for retention_rule in self:
            if retention_rule.activity_id and retention_rule.retention_id.type != 'profit':
                raise Warning(
                    "Para {} no se debe configurar actividad".format(retention_rule.retention_id.name))
            elif not retention_rule.activity_id and retention_rule.retention_id.type == 'profit':
                raise Warning("Para {} se debe configurar actividad".format(retention_rule.retention_id.name))

    @api.constrains('retention_id', 'activity_id')
    def _check_repeat(self):
        for retention_rule in self:
            rules = self.search([
                ('retention_id', '=', retention_rule.retention_id.id),
                ('activity_id', '=', retention_rule.activity_id.id),
                ('id', '!=', retention_rule.id)
            ])
            if rules:
                raise Warning("Existe mas de una regla con actividad {}.".format(
                    retention_rule.activity_id.name if retention_rule.activity_id else "vacia")
                )

    @api.constrains('not_applicable_minimum')
    def _check_not_applicable_minimum(self):
        if any(retention_rule.not_applicable_minimum < 0 for retention_rule in self):
            raise Warning("El minimo no imponible no puede ser negativo.")

    @api.constrains('minimum_tax')
    def _check_minimum_tax(self):
        if any(retention_rule.minimum_tax < 0 for retention_rule in self):
            raise Warning("El impuesto minimo no puede ser negativo.")

    @api.constrains('percentage', 'retention_id')
    def _check_percentage(self):
        if any(retention_rule.percentage < 0 or retention_rule.percentage > 100 for retention_rule in self):
            raise Warning("El porcentaje debe estar entre 0 y 100")

    retention_id = fields.Many2one(
        comodel_name='retention.retention',
        string="Retencion",
        ondelete='cascade',
    )

    activity_id = fields.Many2one(
        comodel_name='retention.activity',
        string="Actividad",
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
    )

    exclude_minimum = fields.Boolean(
        string='Excluir minimo',
        default=False,
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

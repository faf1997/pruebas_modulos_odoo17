# - coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from odoo import models
from odoo.exceptions import ValidationError


class RetentionRetention(models.Model):
    _inherit = 'retention.retention'

    def get_tucuman_retention(self):
        tucuman_retention = self.search([
            ('state_id', '=', self.env.ref('base.state_ar_t').id),
            ('jurisdiction', '=', 'provincial'),
            ('type', '=', 'gross_income'),
            ('type_tax_use', '=', 'purchase'),
            ('company_id', 'in', (self.env.company.id, False))
        ], limit=1)
        if not tucuman_retention:
            raise ValidationError('No se encontro retención de IIBB para Tucumán, por favor crear una')
        return tucuman_retention

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

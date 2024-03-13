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


class PerceptionPerception(models.Model):
    _inherit = 'perception.perception'

    def get_tucuman_perception(self):
        tucuman_perception = self.search([
            ('state_id', '=', self.env.ref('base.state_ar_t').id),
            ('jurisdiction', '=', 'provincial'),
            ('type', '=', 'gross_income'),
            ('type_tax_use', '=', 'sale'),
            ('company_id', 'in', (self.env.company.id, False))
        ], limit=1)
        if not tucuman_perception:
            raise ValidationError('No se encontro percepción de IIBB para Tucumán, por favor crear una')
        return tucuman_perception

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models
from odoo.exceptions import ValidationError


class RetentionRetention(models.Model):

    _inherit = 'retention.retention'

    def get_iibb_pba_retention(self):
        retentions = self.search([
            ('type', '=', 'gross_income'),
            ('jurisdiction', '=', 'provincial'),
            ('state_id', '=', self.env.ref('base.state_ar_b').id),
            ('type_tax_use', '=', 'purchase'),
            ('company_id', 'in', (self.env.company.id, False))
        ])

        if not retentions:
            raise ValidationError("No se encontro retención de IIBB de PBA, por favor, crear una")

        retention = self.env['res.company.retention'].sudo().search([('retention_id', 'in', retentions.ids)])

        return retention.filtered(lambda x: x.company_id == self.env.company).retention_id\
               or (retention and retention[0].retention_id) or retentions[0]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

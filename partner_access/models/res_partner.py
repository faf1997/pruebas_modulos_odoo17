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

from odoo import models, fields


class ResPartner(models.Model):

    _inherit = 'res.partner'

    access_count = fields.Integer(
        compute='_compute_access_count',
        string='# de Accesos'
    )

    def res_partner_to_access(self):
        return {
            'name': 'Accesos',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'res.partner.access',
            'context': {'search_default_partner_id': self.parent_id.id or self.id}
        }

    def _compute_access_count(self):
        for each in self:
            partner = each.parent_id or each
            each.access_count = self.env['res.partner.access'].sudo().search_count([('partner_id', '=', partner.id)])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

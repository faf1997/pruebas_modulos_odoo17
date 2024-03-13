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

from odoo import models, api, fields


class ResPartner(models.Model):

    _inherit = 'res.partner'

    get_wsafip_partner_data = fields.Boolean(
        'Obtener datos de AFIP',
        help='Sobrescribirá los datos fiscales del partner',
    )
    partner_data_error = fields.Boolean(
        'Error al obtener datos de AFIP',
    )

    @api.model
    def create(self, vals):
        vals.update({
            'get_wsafip_partner_data': False,
            'partner_data_error': False,
        })
        return super(ResPartner, self).create(vals)

    def write(self, vals):
        vals.update({
            'get_wsafip_partner_data': False,
            'partner_data_error': False,
        })
        return super(ResPartner, self).write(vals)

    @api.onchange('get_wsafip_partner_data')
    def onchange_get_wsafip_partner_data(self):
        if self.get_wsafip_partner_data:
            try:
                partner_data = self.env['partner.data.get.wizard'].new({
                    'vat': self.vat,
                    'company_id': self.env.company
                })
                vals = partner_data.get_data()
                vals = partner_data.load_vals(vals)
                vals.update({
                    'get_wsafip_partner_data': False,
                    'partner_data_error': False,
                })
                self.update(vals)
            except:
                self.update({
                    'get_wsafip_partner_data': False,
                    'partner_data_error': True,
                })


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

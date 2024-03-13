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

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    cash_flow_date = fields.Date(
        string='Fecha cash flow general'
    )

    def change_cashflow_date(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cambiar fecha de cash flow',
            'view_mode': 'form',
            'view_type': 'form',
            'res_model': 'change.cashflow.date',
            'target': 'new'
        }
    0
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

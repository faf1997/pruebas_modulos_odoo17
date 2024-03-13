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


class ChangeCashflowDate(models.TransientModel):
    _name = 'change.cashflow.date'

    def _get_domain_line(self):
        sale_id = self.env.context.get('active_id')
        return [('order_id', '=', sale_id)]

    date = fields.Date(
        string='Nueva fecha',
        required=True
    )
    line_id = fields.Many2one(
        comodel_name='sale.order.line',
        string='Linea de venta',
        required=True,
        domain=_get_domain_line,
        ondelete='cascade'
    )

    def change_date(self):
        """ Cambia la fecha de cash flow para una linea de venta determinada"""
        for wizard in self:
            wizard.line_id.write({'admission_date': wizard.date})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

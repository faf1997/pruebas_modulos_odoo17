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


class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    def get_cash_flow_values(self, date_from, invoice, cash_flow_id):
        date = max(self.date_maturity or self.date, date_from)
        credit = self.amount_residual if invoice.move_type in ['out_refund', 'in_invoice'] else 0
        debit = self.amount_residual if invoice.move_type in ['out_invoice', 'in_refund'] else 0
        if not self.amount_residual:
            return
        return {
            'credit': abs(credit),
            'debit': abs(debit),
            'date': date,
            'reference': invoice.name_get()[0][1] + ' - ' + invoice.partner_id.name,
            'balance': self.amount_residual,
            'cash_flow_id': cash_flow_id
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

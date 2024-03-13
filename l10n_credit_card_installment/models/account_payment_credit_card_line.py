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


class AccountPaymentCreditCardLine(models.Model):
    _inherit = 'account.payment.credit.card.line'

    def create_installments(self):
        for r in self:
            self.env['credit.card.installment'].generate_from_payment(r)

    def _get_installment_vals(self, installment, amount, due_date):
        self.ensure_one()
        vals = {
            'name': self.name,
            'credit_card_line_id': self.id,
            'total_installments': self.payment_plan_id.quantity,
            'installment': installment,
            'due_date': due_date,
            'amount': amount
        }
        return vals

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

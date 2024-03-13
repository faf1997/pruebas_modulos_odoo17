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


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_draft(self):
        if self.mapped('credit_card_coupon_ids').filtered("credit_card_coupon_reconcile_id"):
            raise ValidationError("No se puede volver a borrador un pago con cupones asociados a una liquidación.")
        return super(AccountPayment, self).action_draft()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

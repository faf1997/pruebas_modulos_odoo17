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


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    credit_card_coupon_ids = fields.One2many(
        comodel_name='credit.card.coupon',
        inverse_name='payment_id',
        string="Cupones"
    )

    def action_post(self):
        self.filtered(lambda l: l.partner_type == 'customer').mapped('credit_card_line_ids').create_coupons()
        return super(AccountPayment, self).action_post()

    def action_draft(self):
        res = super(AccountPayment, self).action_draft()
        self.mapped('credit_card_coupon_ids').unlink()
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

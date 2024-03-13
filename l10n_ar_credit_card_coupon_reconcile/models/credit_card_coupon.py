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

from odoo import models, fields, api


class CreditCardCoupon(models.Model):
    _inherit = 'credit.card.coupon'

    credit_card_coupon_reconcile_id = fields.Many2one(
        comodel_name='credit.card.coupon.reconcile',
        string="Liquidación",
        ondelete='set null',
        readonly=True
    )

    credit_card_coupon_reconcile_currency_id = fields.Many2one(
        related='credit_card_coupon_reconcile_id.currency_id',
        string="Moneda de liquidación",
    )

    amount_reconcile_currency = fields.Monetary(
        string="Monto en moneda de liquidación",
        currency_field='credit_card_coupon_reconcile_currency_id',
        compute='_get_amount_in_reconcile_currency'
    )

    state = fields.Selection(selection_add=[('settled','Liquidado')])

    def convert_coupon_amount(self, amount, from_currency, to_currency, company, date):
        return from_currency._convert(amount, to_currency, company, date)

    @api.depends('amount', 'credit_card_coupon_reconcile_currency_id', 'currency_id')
    def _get_amount_in_reconcile_currency(self):
        for coupon in self:
            reconcile = coupon.credit_card_coupon_reconcile_id
            coupon.amount_reconcile_currency = coupon.convert_coupon_amount(coupon.amount,
                                                                            coupon.currency_id,
                                                                            coupon.credit_card_coupon_reconcile_currency_id, 
                                                                            reconcile.company_id, reconcile.acreditation_date)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

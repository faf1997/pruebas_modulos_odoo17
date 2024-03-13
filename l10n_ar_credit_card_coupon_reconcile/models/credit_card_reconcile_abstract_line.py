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
from odoo.exceptions import ValidationError


class CreditCardCouponReconcileAbstractLine(models.AbstractModel):
    _name = "credit.card.coupon.reconcile.abstract.line"
    _description = "Detalle de líneas en Liquidación de Cupones de Tarjetas de Crédito"

    credit_card_coupon_reconcile_id = fields.Many2one(
        comodel_name='credit.card.coupon.reconcile',
        string="Liquidación",
        ondelete='cascade',
        required=True
    )

    currency_id = fields.Many2one(
        related='credit_card_coupon_reconcile_id.currency_id',
        readonly=True,
        store=True
    )

    company_id = fields.Many2one(
        related='credit_card_coupon_reconcile_id.company_id',
        readonly=True,
        store=True
    )

    amount = fields.Float(
        string='Monto',
        required=True
    )

    @api.constrains('amount')
    def check_negative_amounts(self):
        if any(r.amount < 0 for r in self):
            raise ValidationError("Monto no puede ser negativo.")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

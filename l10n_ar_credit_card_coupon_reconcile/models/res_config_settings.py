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


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    credit_card_coupon_reconcile_discount_product_id = fields.Many2one(
        related='company_id.credit_card_coupon_reconcile_discount_product_id',
        readonly=False
    )
    credit_card_coupon_reconcile_receivable_journal_id = fields.Many2one(
        related='company_id.credit_card_coupon_reconcile_receivable_journal_id',
        domain="[('company_id', '=', company_id),('type', 'in', ['bank', 'cash']),\
        ('payment_usage', '=', 'payment_type')]",
        help="Diario utilizado como método de pago del pago de cliente en la liquidación",
        readonly=False
    )
    credit_card_coupon_reconcile_journal_id = fields.Many2one(
        related='company_id.credit_card_coupon_reconcile_journal_id',
        domain="[('company_id', '=', company_id),('type', 'in', ['bank', 'cash'])]",
        help="Diario utilizado en la liquidación",
        readonly=False
    )
    credit_card_coupon_reconcile_supplier_journal_id = fields.Many2one(
        related='company_id.credit_card_coupon_reconcile_supplier_journal_id',
        domain="[('company_id', '=', company_id),('type', 'in', ['bank', 'cash']),\
        ('payment_usage', '!=', 'document_book')]",
        help="Diario utilizado en el pago de proveedor de la liquidación",
        readonly=False
    )
    credit_card_coupon_reconcile_coupons_account_id = fields.Many2one(
        related='company_id.credit_card_coupon_reconcile_coupons_account_id',
        domain="[('company_id', '=', company_id)]",
        help="Cuenta de cupones utilizada en el recibo de venta de la liquidación",
        readonly=False
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

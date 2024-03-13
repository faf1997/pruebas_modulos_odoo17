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


class ResCompany(models.Model):
    _inherit = 'res.company'

    credit_card_coupon_reconcile_discount_product_id = fields.Many2one(
        comodel_name='product.product', 
        string='Producto "descuentos ganados"',
    )
    credit_card_coupon_reconcile_receivable_journal_id = fields.Many2one(
        comodel_name='account.journal', 
        string='Método de pago', 
        domain="[('company_id', '=', id),('type', 'in', ['bank', 'cash']),\
        ('payment_usage', '=', 'payment_type')]"
    )
    credit_card_coupon_reconcile_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Diario',
        domain="[('company_id', '=', id),('type', 'in', ['bank', 'cash'])]",
    )
    credit_card_coupon_reconcile_supplier_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Diario de pago de proveedor',
        domain="[('company_id', '=', id),('type', 'in', ['bank', 'cash']),\
        ('payment_usage', '!=', 'document_book')]",
    )
    credit_card_coupon_reconcile_coupons_account_id = fields.Many2one(
        comodel_name='account.account',
        string="Cuenta de cupones",
        domain="[('company_id', '=', id)]",
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

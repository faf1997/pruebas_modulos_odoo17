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


class CreditCardCouponReconcileTaxLine(models.Model):
    _name = "credit.card.coupon.reconcile.tax.line"
    _inherit = "credit.card.coupon.reconcile.abstract.line"
    _description = "Detalle de Impuestos en Liquidación de Cupones de Tarjetas de Crédito"

    tax_id = fields.Many2one(
        comodel_name='account.tax', 
        string='Impuesto', 
        domain=lambda self: self._domain_tax_id(),
        required=True,
        check_company=True
    )

    is_exempt = fields.Boolean(
        related='tax_id.is_exempt'
    )

    base = fields.Float(
        string='Base'
    )

    @api.model
    def _domain_tax_id(self):
        tax_group_taxes = self.env.ref('account.tax_group_taxes')
        domain = "[('company_id', '=', company_id),('type_tax_use', '=', 'purchase'), '|', '|',\
        ('is_vat', '=', True), ('is_exempt', '=', True), ('tax_group_id', '=', {})]".format(tax_group_taxes.id)
        return domain

    @api.constrains('base')
    def check_negative_base(self):
        if any(r.base <= 0 and not r.is_exempt for r in self):
            raise ValidationError("Base tiene que ser estrictamente positivo.")
    
    @api.onchange('amount')
    def onchange_compute_base(self):
        self.base = round(self.amount / (self.tax_id.amount / 100), 4) if self.tax_id and self.tax_id.amount else 0

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

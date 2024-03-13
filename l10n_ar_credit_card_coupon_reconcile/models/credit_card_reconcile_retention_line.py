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


class CreditCardCouponReconcileRetentionLine(models.Model):
    _name = "credit.card.coupon.reconcile.retention.line"
    _inherit = "credit.card.coupon.reconcile.abstract.line"
    _description = "Detalle de Retenciones en Liquidación de Cupones de Tarjetas de Crédito"

    journal_id = fields.Many2one(
        comodel_name="account.journal",
        string="Diario retención",
        domain="[('company_id', '=', company_id),('currency_id', '=', currency_id),\
        ('type', 'in', ['bank', 'cash']),('payment_usage', '=', 'retention')]",
        required=True,
        default=lambda self: self._get_default_retention_journal_id(),
        check_company=True
    )

    retention_id = fields.Many2one(
        comodel_name='retention.retention', 
        string='Retención',
        domain="[('company_id', '=', company_id),('type_tax_use', '=', 'sale')]",
        required=True,
        check_company=True
    )

    def _get_default_retention_journal_id(self):
        company = self.env['res.company'].browse(self._context.get('default_company_id', self.env.company.id))
        return company.account_payment_retention_journal_id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
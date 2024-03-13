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


class CreditCardCouponReconcileWizard(models.TransientModel):
    _name = 'credit.card.coupon.reconcile.wizard'
    _description = "Wizard para la liquidación de tarjetas de crédito"
    
    credit_card_coupon_reconcile_name = fields.Char(
        string="Número de liquidación", 
        required=True
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string="Partner bancario",
        required=True
    )
    acreditation_date = fields.Date(
        string="Fecha de acreditación", 
        default=fields.Date.context_today,
        required=True
    )
    company_id = fields.Many2one(
        comodel_name='res.company', 
        string="Compañía", 
        required=True, 
        default=lambda self: self.env.company
    )
    journal_id = fields.Many2one(
        comodel_name='account.journal', 
        string="Diario",
        domain="[('company_id', '=', company_id),('type', 'in', ['bank', 'cash'])]", 
        required=True,
        default=lambda self: self._get_default_journal()
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda',
        related='journal_id.currency_id'
    )
    origin = fields.Char(
        string="Documento de origen"
    )
    amount = fields.Monetary(
        string="Total a liquidar",
        currency_field="currency_id",
        readonly=True
    )

    def _get_default_journal(self):
        return self.env.company.credit_card_coupon_reconcile_journal_id

    def _get_coupons_total(self):
        credit_card_coupon_proxy = self.env['credit.card.coupon']
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        total = sum(coupon.convert_coupon_amount(coupon.amount, coupon.currency_id, 
                                                 self.journal_id.currency_id or self.company_id.currency_id,
                                                 self.company_id, self.acreditation_date) for coupon in credit_card_coupon_proxy.browse(active_ids))            
        return total
    
    @api.onchange('company_id')
    def onchange_company_id(self):
        self.journal_id = self.company_id.credit_card_coupon_reconcile_journal_id
    
    @api.onchange('journal_id', 'acreditation_date')
    def onchange_journal_id(self):
        self.amount = 0.0
        if self.journal_id and self.acreditation_date:
            self.amount = self._get_coupons_total()        

    def get_reconcile_vals(self, coupon_ids):
        return {
            'origin': self.origin,
            'journal_id': self.journal_id.id,
            'partner_id': self.partner_id.id,
            'name': self.credit_card_coupon_reconcile_name,
            'acreditation_date': self.acreditation_date,
            'credit_card_coupon_ids': [(6, 0, coupon_ids)]
        }

    def create_reconcile(self):
        credit_card_coupon_reconcile_proxy = self.env['credit.card.coupon.reconcile']
        credit_card_coupon_proxy = self.env['credit.card.coupon']

        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        
        for coupon in credit_card_coupon_proxy.browse(active_ids):    
            if coupon.credit_card_coupon_reconcile_id:
                raise ValidationError("El cupón {} ya fue liquidado por la liquidación {}".format(coupon.name, 
                                                                                                   coupon.credit_card_coupon_reconcile_id.name))
        reconcile_id = credit_card_coupon_reconcile_proxy.with_context(force_company=self.company_id.id).create(self.get_reconcile_vals(active_ids))

        form_view_id = self.env.ref('l10n_ar_credit_card_coupon_reconcile.credit_card_coupon_reconcile_form').id

        return {
            'type': 'ir.actions.act_window',
            'views': [[form_view_id, 'form']],
            'res_model': 'credit.card.coupon.reconcile',
            'res_id': reconcile_id.id,
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

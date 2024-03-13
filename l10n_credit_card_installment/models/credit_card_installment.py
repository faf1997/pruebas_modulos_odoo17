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
from dateutil.relativedelta import relativedelta


class CreditCardInstallment(models.Model):
    _name = 'credit.card.installment'
    _description = "Cuota de tarjeta de crédito"
    _order = 'due_date asc'

    name = fields.Char(
        'Descripción'
    )
    credit_card_line_id = fields.Many2one(
        'account.payment.credit.card.line',
        'Línea de pago'
    )
    partner_id = fields.Many2one(
        related='payment_id.partner_id'
    )
    credit_card_id = fields.Many2one(
        related='credit_card_line_id.credit_card_id',
        store=True
    )
    payment_id = fields.Many2one(
        related='credit_card_line_id.payment_id'
    )
    currency_id = fields.Many2one(
        related='credit_card_line_id.currency_id'
    )
    total_installments = fields.Integer(
        'Total de cuotas'
    )
    installment = fields.Integer(
        'Cuota'
    )
    amount = fields.Monetary(
        'Importe'
    )
    due_date = fields.Date(
        'Fecha de vencimiento'
    )
    installments_text = fields.Char(
        'Detalle de cuota',
        compute='_compute_installments_text'
    )
    company_id = fields.Many2one(
        related='payment_id.company_id'
    )

    def _compute_installments_text(self):
        for line in self:
            line.installments_text = '{} / {}'.format(line.installment, line.total_installments)

    def generate_from_payment(self, payment_line):
        accumulated = 0
        installments = payment_line.payment_plan_id.quantity
        for installment in range(1, installments + 1):
            due_date = fields.Date.from_string(payment_line.payment_id.date) + relativedelta(months=+(installment-1))
            # La ultima cuota es el restante entre el total y las anteriores
            amount = round(payment_line.amount / installments, 2) if installment != installments else round(payment_line.amount - accumulated, 2)
            self.create(payment_line._get_installment_vals(installment, amount, due_date))
            accumulated += amount

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

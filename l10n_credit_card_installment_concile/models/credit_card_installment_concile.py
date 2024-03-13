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


class CreditCardInstallmentConcile(models.Model):
    _name = 'credit.card.installment.concile'
    _description = "Conciliación de cuotas de tarjeta de crédito"

    @api.depends('installment_ids')
    def _get_conciliation_total(self):
        for each in self:
            each.amount = sum(installment.amount for installment in each.installment_ids)

    name = fields.Char(
        'Nombre',
        required=True
    )
    date = fields.Date(
        'Fecha de conciliación',
        required=True
    )
    date_from = fields.Date(
        'Fecha desde',
        required=True
    )
    date_to = fields.Date(
        'Fecha hasta',
        required=True
    )
    journal_id = fields.Many2one(
        'account.journal',
        'Cuenta Bancaria',
        required=True,
        ondelete='restrict'
    )
    credit_card_id = fields.Many2one(
        'credit.card',
        'Tarjeta',
        required=True,
        ondelete='restrict'
    )
    amount = fields.Monetary(
        'Importe total',
        compute='_get_conciliation_total',
    )
    currency_id = fields.Many2one(
        'res.currency',
        'Moneda'
    )
    installment_ids = fields.Many2many(
        'credit.card.installment',
        'credit_card_installment_concile_rel',
        'concile_id',
        'installment_id',
        string='Cuotas'
    )
    state = fields.Selection(
        [('canceled', 'Cancelada'),
         ('draft', 'Borrador'),
         ('reconciled', 'Conciliada')],
        string='Estado',
        default='draft',
    )
    move_id = fields.Many2one(
        'account.move',
        'Asiento contable',
        readonly=True,
        ondelete='restrict'
    )
    company_id = fields.Many2one(
        'res.company',
        string='Compañía',
        required=True,
        default=lambda self: self.env.user.company_id,
    )

    _sql_constraints = [('name_uniq', 'unique(name,company_id)', 'El nombre de la conciliacion debe ser unico')]
    _order = "date_from desc, name desc"

    @api.constrains('date_from', 'date_to')
    def constraint_dates(self):
        for conciliation in self:
            if conciliation.date_from > conciliation.date_to:
                raise ValidationError("La fecha desde debe ser menor que la fecha hasta.")

    @api.constrains('installment_ids')
    def constraint_installments(self):
        for conciliation in self:
            if len(conciliation.installment_ids.mapped('currency_id')) > 1:
                raise ValidationError("Las conciliaciones deben ser de cuotas en la misma moneda.")
            if len(conciliation.installment_ids.mapped('credit_card_id')) > 1:
                raise ValidationError("Las conciliaciones deben ser de cuotas de la misma tarjeta.")

    def post(self):
        for conciliation in self:
            if not conciliation.installment_ids:
                raise ValidationError("No se puede validar una conciliación sin cuotas.")

            conciliation.write({
                # Ya validamos en el constraint que la moneda es unica
                'currency_id': conciliation.installment_ids.mapped('currency_id').id,
                'state': 'reconciled'
            })
            conciliation.move_id = conciliation.create_move()
            conciliation.installment_ids.reconcile()

    def cancel(self):
        for conciliation in self:
            move = conciliation.move_id
            conciliation.move_id = None
            move.button_cancel()
            move.unlink()
            conciliation.installment_ids.cancel_reconcile()
            conciliation.state = 'canceled'

    def cancel_to_draft(self):
        self.write({'state': 'draft'})

    def create_move(self):
        self.ensure_one()

        vals = {
            'date': self.date,
            'ref': 'Conciliacion de tarjetas: ' + self.name,
            'journal_id': self.journal_id.id,
        }
        move = self.env['account.move'].create(vals)

        # Hacemos el computo multimoneda
        company = self.env.user.company_id
        debit = self.currency_id._convert(self.amount, company.currency_id, company, self.date)
        amount_currency = self.amount if self.currency_id != company.currency_id else False

        # Creamos las lineas de los asientos
        self._create_move_lines(move, self.company_id.transfer_account_id, amount_currency, debit=debit)
        self._create_move_lines(move, self.journal_id._get_journal_inbound_outstanding_payment_accounts()[0], -amount_currency, credit=debit)
        move.post()
        return move

    def _create_move_lines(self, move, account, amount_currency, debit=0.0, credit=0.0):
        """
        Crea una move line de la boleta de deposito y las asocia al move
        :param move: account.move - Asiento a relacionar las move_lines creadas
        :param debit: Importe en el haber de la move line
        :param credit: Importe en el haber de la move line
        :return: account.move.line creada
        """

        if not account:
            raise ValidationError("Falta configurar la cuenta de depósito en la cuenta bancaria"
                                  " o las cuentas en el diario del cheque.")

        company_currency = self.env.user.company_id.currency_id

        move_line_vals = {
            'move_id': move.id,
            'debit': debit,
            'credit': credit,
            'amount_currency': amount_currency,
            'name': move.ref,
            'account_id': account.id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != company_currency and self.currency_id.id or False,
            'ref': move.ref
        }
        return self.env['account.move.line'].with_context(check_move_validity=False).create(move_line_vals)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

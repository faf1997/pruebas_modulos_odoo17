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


class AutomaticDebitFile(models.Model):
    _name = 'automatic.debit.file'
    _description = 'Archivos para debito automatico'

    generation_datetime = fields.Datetime(
        'Fecha de generación del archivo',
        default=fields.Datetime.now()
    )
    date_from = fields.Date(
        string='Desde'
    )
    date_to = fields.Date(
        string='Hasta'
    )
    payment_term_id = fields.Many2one(
        comodel_name='account.payment.term',
        string='Plazo de pago'
    )
    state = fields.Selection(
        selection=[
            ('pending', 'Pendiente'),
            ('confirmed', 'Confirmado'),
            ('rejected', 'Rechazado'),
        ],
        string='Estado',
        default='pending'
    )
    file = fields.Binary(
        string='Archivo',
        filename="filename"
    )
    filename = fields.Char(
        string='Nombre Archivo'
    )
    note = fields.Char(
        string='Notas'
    )
    invoice_ids = fields.One2many(
        comodel_name='account.invoice.file',
        inverse_name='debit_file_id',
        string='Facturas'
    )
    payment_type_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Método de pago',
        domain=[('payment_usage', '=', 'payment_type')],
    )
    payment_journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Diario de pago',
        domain=[('payment_usage', '=', 'document_book')],
    )
    payment_ids = fields.Many2many(
        comodel_name='account.payment',
        string='Pagos'
    )
    invoice_to_pay = fields.Boolean(
        string='Facturas a pagar',
        compute='compute_invoice_to_pay'
    )

    def action_rejected(self):
        """ Pasa al estado rechazado """
        self.ensure_one()
        if self.payment_ids:
            raise ValidationError('Primero debe eliminar los pagos asociados.')
        self.state = 'rejected'

    def action_pending(self):
        """ Pasa al estado pendiente """
        self.ensure_one()
        if self.payment_ids:
            raise ValidationError('Primero debe eliminar los pagos asociados.')
        self.state = 'pending'
        self.invoice_ids.write({'to_pay': True})

    def action_confirm(self):
        """ Pasa al estado confirmado """
        self.ensure_one()
        if not self.payment_journal_id and self.payment_type_journal_id:
            raise ValidationError('Antes de pasar a confirmado debe completar el Diario de pago y Metodo de pago.')
        if self.payment_ids:
            raise ValidationError('Primero debe eliminar los pagos asociados.')
        self.state = 'confirmed'

    @api.depends('invoice_ids', 'invoice_ids.to_pay')
    def compute_invoice_to_pay(self):
        for file in self:
            file.invoice_to_pay = True if file.invoice_ids.filtered(lambda x: x.to_pay) else False

    def create_payment(self, file_invoice):
        """ Genero pago para la factura enviada """
        payment = self.env['account.payment'].create({
            'partner_id': file_invoice.invoice_id.partner_id.id,
            'payment_type': 'inbound',
            'partner_type': 'customer',
            'payment_method_id': self.env.ref('account.account_payment_method_manual_in').id,
            'amount': file_invoice.invoice_id.amount_residual,
            'ref': "Pago por débito aut. de: {}".format(file_invoice.invoice_id.name_get()[0][1]),
            'journal_id': self.payment_journal_id.id,
        })
        # payment.pos_ar_id = payment.get_pos(payment.payment_type)
        self.env['account.payment.type.line'].create({
            'journal_id': self.payment_type_journal_id.id,
            'payment_id': payment.id,
            'amount': file_invoice.invoice_id.amount_residual,
            'payment_currency_amount': file_invoice.invoice_id.amount_residual
        })
        self.env['payment.imputation.line'].create({
            'payment_id': payment.id,
            'move_line_id': file_invoice.invoice_id.line_ids.filtered(
                lambda x: x.account_id.user_type_id.type in ['receivable', 'payable']).id,
            'amount': file_invoice.invoice_id.amount_residual,
        })
        return payment

    def generate_payments(self):
        """ Genero los pagos para las facturas que estan marcadas para pagar """
        self.ensure_one()
        # Filtro las facturas que son para pagar
        invoices_to_pay = self.invoice_ids.filtered(lambda x: x.to_pay)
        payments = self.env['account.payment']
        # Genero el pago para cada factura
        for invoice in invoices_to_pay:
            payment = self.create_payment(invoice)
            # Escribo que fue pagada
            invoice.write({
                'to_pay': False,
                'payment_id': payment.id,
            })
            payments |= payment
        # Asigno los pagos al registro de debito automatico
        self.payment_ids = payments

    def action_view_payments(self):
        return {
            'name': 'Pagos',
            'views': [[False, "tree"], [False, "form"]],
            'domain': [('id', 'in', self.payment_ids.ids)],
            'res_model': 'account.payment',
            'type': 'ir.actions.act_window',
        }

    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, "{} {}".format(
                rec.generation_datetime,
                dict(rec.payment_term_id._fields['card_type'].selection).get(rec.payment_term_id.card_type)
            )))
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

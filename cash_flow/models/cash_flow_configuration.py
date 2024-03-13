# - coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


WEEKDAYS_DELTA = {
    5: 2,
    6: 1,
}


class CashFlowConfiguration(models.Model):
    _name = 'cash.flow.configuration'
    _description = 'Configuración de cashflow'

    qty_days = fields.Integer(
        string='Cantidad de días',
        default=30
    )
    name = fields.Char(
        string='Nombre',
        default='Configuracion'
    )
    account_ids = fields.Many2many(
        relation='cashflow_config_account',
        comodel_name='account.account',
        domain=[('user_type_id.type', '!=', 'view')],
        string='Cuentas'
    )

    account_with_due_date_ids = fields.Many2many(
        relation='cashflow_config_account_with_due_date',
        comodel_name='account.account',
        domain=[('user_type_id.type', '!=', 'view')],
        string='Cuentas'
    )

    third_checks = fields.Boolean(
        string='Cheques de terceros'
    )
    customer_invoices = fields.Boolean(
        string='Documentos de clientes',
        help='Para incluir facturas, notas de debito y credito de clientes'
    )
    supplier_invoices = fields.Boolean(
        string='Documentos de proveedores',
        help='Para incluir facturas, notas de debito y credito de proveedores'
    )
    issued_checks_unconciled = fields.Boolean(
        string='Cheques propios sin conciliar'
    )

    @api.constrains('qty_days')
    def constraint_qty_days(self):
        for config in self:
            if config.qty_days < 1:
                raise ValidationError("La cantidad de días debe ser mayor a 0.")

    def get_values(self, date_from, date_to, cash_flow_id):
        """ Obtengo los valores para generar las lineas """
        values = self._set_account_values(cash_flow_id, date_from)
        values += self._set_account_with_due_date_values(cash_flow_id, date_from, date_to)
        # Cheques terceros
        if self.third_checks:
            checks = self.env['account.third.check'].search([
                ('state', '=', 'wallet'),
                ('amount', '>', 0),
            ])
            values += self._get_check_values(date_from, date_to, checks, cash_flow_id)
        # Cheques propios sin conciliar
        if self.issued_checks_unconciled:
            checks = self.env['account.own.check'].search([
                ('state', 'in', ['collect', 'handed']),
                ('amount', '>', 0),
            ])
            values += self._get_check_values(date_from, date_to, checks, cash_flow_id)
        # Facturas
        if self.customer_invoices or self.supplier_invoices:
            invoices_customer = ['out_refund', 'out_invoice'] if self.customer_invoices else []
            invoices_supplier = ['in_refund', 'in_invoice'] if self.supplier_invoices else []
            invoices = self._get_invoice_values(date_to, invoices_customer + invoices_supplier)
            values += self._set_invoice_values(date_from, invoices, cash_flow_id)
        return values

    def _compute(self, date_from, date_to, cash_flow_id):
        """Genera las lineas segun la configuracion"""
        values = self.get_values(date_from, date_to, cash_flow_id)
        # Creacion de lineas
        self.create_lines(values)

    # Cuentas
    def _set_account_values(self, cash_flow_id, date_from):
        """
        Crea las lineas en el cash flow por cada cuenta de la configuracion
        """
        list_values = []
        # Iteramos por las cuentas de la configuracion
        for account in self.account_ids:

            # Calculamos el credito y debito
            move_lines = self.search_past_move_lines(account, date_from)
            balance = self.calculate_balance(move_lines)
            if not balance:
                continue
            credit = -balance if balance < 0 else 0
            debit = balance if balance > 0 else 0

            # Se generan las lineas para el cashflow
            list_values.append({
                'date': date_from,
                'credit': credit,
                'debit': debit,
                'balance': balance,
                'reference': account.name,
                'cash_flow_id': cash_flow_id,
            })
        return list_values

    def _set_account_with_due_date_values(self, cash_flow_id, date_from, date_to):
        """
        Crea las lineas en el cash flow por cada cuenta de la configuracion teniendo en cuenta fecha de vencimiento
        """
        list_values = []
        # Iteramos por las cuentas de la configuracion
        for account in self.account_with_due_date_ids:

            for line in self.search_future_move_lines(account, date_from, date_to):

                balance = self.calculate_balance(line)
                if not balance:
                    continue
                credit = -balance if balance < 0 else 0
                debit = balance if balance > 0 else 0

                date = max(line.date_maturity, date_from)

                # Se generan las lineas para el cashflow
                list_values.append({
                    'date': date,
                    'credit': credit,
                    'debit': debit,
                    'balance': balance,
                    'reference': '{}: {}'.format(line.account_id.name, line.name or 'Sin referencia'),
                    'cash_flow_id': cash_flow_id,
                })
        return list_values

    def search_past_move_lines(self, account, date_from):
        """Busco las lineas de asientos pasados para la cuenta"""
        return self.env['account.move.line'].search([
            ('account_id', '=', account.id),
            ('date', '<=', date_from),
            ('move_id.state', '=', 'posted')
        ])

    def search_future_move_lines(self, account, date_from, date_to):
        """Busco las lineas de asientos futuros para la cuenta"""
        return self.env['account.move.line'].search([
            ('account_id', '=', account.id),
            ('date_maturity', '>', date_from),
            ('date_maturity', '<=', date_to),
            ('move_id.state', '=', 'posted')
        ])

    @staticmethod
    def calculate_balance(move_lines):
        """Calculamos el balance de una cuenta"""
        account_debit = sum(move.debit for move in move_lines.filtered(lambda x: x.debit > 0))
        account_credit = sum(move.credit for move in move_lines.filtered(lambda x: x.credit > 0))
        return account_debit - account_credit

    # Facturas
    def _set_invoice_values(self, date_from, invoices, cash_flow_id):
        """Segun el tipo de factura calculamos el debito o credito y generamos la linea para la misma"""
        list_values = []
        for invoice in invoices:
            for line in invoice.line_ids.filtered(
                lambda x: x.account_id.user_type_id.type in ['receivable', 'payable']
            ):
                values = line.get_cash_flow_values(date_from, invoice, cash_flow_id)
                if values:
                    list_values.append(values)
        return list_values

    def _get_invoice_values(self, date_to, invoice_type):
        """Busco las facturas abiertas menores a la fecha fin
        :param date_to: Fecha fin del cash flow
        :param invoice_type: Tipos de facturas
        :return: record de facturas encontradas
        """
        invoice_type = ('move_type', 'in', invoice_type)
        invoices_due = self.env['account.move'].search([
            ('invoice_date_due', '<=', date_to),
            ('amount_residual', '>', 0),
            ('state', '=', 'posted'),
            ('payment_state', '!=', 'paid'),
            invoice_type,
        ])
        return invoices_due

    # Cheques
    @staticmethod
    def _get_check_values(date_from, date_to, account_checks, cash_flow_id):
        """Se obtienen los cheques para el rango de fechas
        :param date_from: Fecha de inicio
        :param date_to: Fecha de fin
        :return: Lista de cheques
        """

        checks = []
        # Se buscan los cheques y se contempla casos de fin de semana
        for check in account_checks:

            # Si el cheque no tiene alguna de las fechas lo salteamos
            if not (check.payment_date and check.issue_date):
                continue
            payment_date = check.payment_date or check.issue_date
            check_date = payment_date
            # Se saltean dias basado a si es sabado o domingo
            check_date += relativedelta(days=WEEKDAYS_DELTA.get(check_date.weekday(), 0))
            # Se agrega clearing
            check_date += relativedelta(days=1)
            # Se vuelven saltear dias basado a si es sabado o domingo luego de sumado el clearing
            check_date += relativedelta(days=WEEKDAYS_DELTA.get(check_date.weekday(), 0))

            # Seteo la fecha en el cheque
            check_date = check_date if check_date >= date_from else date_from
            # Si la fecha coincide con el rango se agrega el cheque
            if date_from <= check_date <= date_to:
                reference = 'Cheque propio pendiente de debitar N° ' if check._name == 'account.own.check' else 'Cheque de tercero a depositar N° '
                checks.append({
                    'reference': reference + str(check.name),
                    'credit': check.amount if check._name == 'account.own.check' else 0,
                    'debit': check.amount if check._name == 'account.third.check' else 0,
                    'date': check_date,
                    'balance': -check.amount if check._name == 'account.own.check' else check.amount,
                    'cash_flow_id': cash_flow_id
                })

        return checks

    def create_lines(self, values):
        """Creacion de lineas
        :param values: Lista de diccionarios"""
        for val in values:
            if val.get('balance'):
                self.env['account.cash.flow.line'].create(val)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

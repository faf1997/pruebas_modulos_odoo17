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


from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from ..models import retention_retention
from odoo.exceptions import ValidationError


def get_accumulated_payments(model, partner, date):
    """
    Busca los pagos para ese partner del periodo (principio y fin de mes de la fecha)
    :param model: models.Model()
    :param partner: res.partner del cual se buscaran los pagos
    :param date: Fecha de la cual se considerará el periodo
    """
    payments = model.env['account.payment'].search([
        ('payment_type', '=', 'outbound'),
        ('partner_type', '=', 'supplier'),
        ('partner_id', '=', partner.id),
        ('state', 'not in', ['draft', 'cancelled']),
        ('date', '>=', fields.Date.to_string(date.replace(day=1))),
        ('date', '<', fields.Date.to_string(date.replace(day=1) + relativedelta(months=1))),
        ('company_id', '=', model.company_id.id or model.env.company.id),
    ])

    return payments


class AccountPayment(models.AbstractModel):
    _inherit = 'account.payment'

    @api.onchange('partner_id')
    def onchange_partner_imputation(self):
        super(AccountPayment, self).onchange_partner_imputation()
        """ Para los casos que se paga una o mas facturas, pero se preseleccionan """
        if self.should_generate_retentions() and self.env.context.get('active_model') == 'account.move':
            self.create_retentions()
    
    def should_generate_retentions(self):
        self.ensure_one()
        return self.payment_type == 'outbound' and self.partner_type == 'supplier'

    def get_amount_to_tax(self):
        """
        Busca el importe a retener en base a las imputaciones realizadas
        :return: Importe a retener
        """
        self.ensure_one()

        retention_currency = self.company_id.account_payment_retention_journal_id.currency_id or \
            self.company_id.currency_id

        amount = self.currency_id._convert(
            self.advance_amount,
            retention_currency,
            self.company_id,
            self.date
        ) if self.advance_amount else 0.0

        for imputation in self.payment_imputation_ids:
            invoice = imputation.move_line_id.move_id
            imputation_amount = imputation.currency_id._convert(
                imputation.amount,
                retention_currency,
                self.company_id,
                self.date
            )
            # Para facturas A retenemos importes gravados o exentos, si no, el total.
            if invoice and invoice.voucher_type_id.denomination_id.vat_discriminated:
                if invoice.amount_to_tax or invoice.amount_exempt:
                    amount += imputation_amount /\
                              (invoice.amount_total / (invoice.amount_to_tax + invoice.amount_exempt))
            else:
                # Si no tiene factura solo me interesa el total imputado
                amount += imputation_amount

        return amount

    def create_retentions(self):
        """
        Crea las retenciones para el pago en base a lo que se va a pagar y la configuracion de la empresa
        """
        for payment in self:
            base = payment.with_context(
                fixed_rate=payment.currency_rate,
                fixed_from_currency=payment.currency_id,
                fixed_to_currency=payment.company_id.currency_id
            ).get_amount_to_tax()
            payment.retention_ids = [(5, 0, 0)]
            retentions = []
            for retention in payment.company_id.retention_ids:
                retention = retention.retention_id
                # Hacemos el calculo para cada retencion
                functions = retention_retention.RETENTIONS_CALCULATION_FUNCTIONS
                try:
                    ret_value = getattr(
                        retention, functions.get(retention.type))(
                        payment.partner_id, base, payment
                    )
                except TypeError:
                    raise ValidationError(
                        "No se encontró cálculo automático para retención: {}.\n "
                        "Por favor, desconfigure la retención de la empresa.".format(
                            dict(retention._fields['type']._description_selection(self.env)).get(retention.type)
                        )
                    )
                except Exception as e:
                    raise ValidationError(e.args)
                # Creamos la retencion en caso que el importe calculado sea mayor que 0
                if ret_value and round(ret_value[1], 2) > 0:
                    vals = payment._create_retention(ret_value[0], ret_value[1], retention)
                    retentions.append((0, 0, vals))

            payment.retention_ids = retentions
            # Actualizamos los valores en los casos que haya cotizacion
            for retention in payment.retention_ids:
                retention.onchange_update_rate()
                retention.onchange_amount()
            payment.onchange_retention_ids()

    def _create_retention(self, base, amount, retention):
        """ Crea una linea de retencion en el pago """
        self.ensure_one()
        vals = {
            'base': base,
            'aliquot': round((amount/base)*100 if base else 0.0, 2),
            'journal_id': retention.company_id.account_payment_retention_journal_id.id if retention.company_id else self.journal_id.company_id.account_payment_retention_journal_id.id,
            'amount': self.env['account.payment.retention'].round_half_up(amount, 2),
            'retention_id': retention.id,
            'name': retention.name,
            'jurisdiction': retention.jurisdiction
        }

        if retention.type == 'profit':
            rule = retention.get_profit_retention_rule(self.partner_id)
            if rule:
                vals['activity_id'] = rule.activity_id.id

        return vals

    def get_accumulated_amount(self):
        """ Busca el acumulado de los pagos, considerando los netos gravados de las facturas que se pagaron """
        accumulated = 0
        for payment in self:
            payment_move_lines = payment.env['account.move.line'].search([('payment_id', '=', payment.id)]).filtered(
                lambda x: x.debit > 0 and x.account_id.internal_type == 'payable')
            debit = sum(payment_move_lines.mapped('debit'))
            accumulated += debit
            amount_curr = sum(payment_move_lines.mapped('amount_currency'))
            rate = debit / amount_curr if amount_curr else 1
            payment._compute_stat_buttons_from_reconciliation()
            for invoice in payment.payment_imputation_ids.mapped('move_line_id.move_id'):
                amount = 0
                # Busco entre las conciliaciones realizadas a la factura las que correspondan al pago actual, y sumo
                # los importes convertidos según la cotización del pago
                for reconciled_value in invoice._get_reconciled_info_JSON_values():
                    if reconciled_value.get("account_payment_id") == payment.id:
                        amount += reconciled_value.get("amount", 0.0) * rate
                # Para facturas A retenemos importes gravados o exentos, si no, el total
                if invoice.voucher_type_id.denomination_id.vat_discriminated:
                    # Sacamos la diferencia entre los impuestos y la factura, ya que se retiene sobre el neto gravado
                    if invoice.amount_to_tax or invoice.amount_exempt:
                        invoice_tax = invoice.amount_total / (invoice.amount_to_tax + invoice.amount_exempt)
                    else:
                        invoice_tax = None
                    # En ese caso le restamos al importe pagado la parte de impuestos, si no, no se retiene
                    accumulated -= amount - (amount / invoice_tax) if invoice_tax else amount

        return accumulated

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

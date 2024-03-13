# -*- coding: utf-8 -*

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import date
from dateutil.relativedelta import relativedelta
from l10n_ar_api.documents import tribute
import logging

_logger = logging.getLogger(__name__)

class ResPartner(models.Model):
    _inherit = 'res.partner'

    income_wh_registration = fields.Selection(
        [('1', 'Activo'),('2','No Registrado'),('3','Exento'),('4','No Corresponde')],
        string="Insc. Reg. Ganancias",
        required=True,
        default='1',
    )
class AccountPayment(models.AbstractModel):
    _inherit = 'account.payment'

    def get_accumulated_amount_pay_currency(self):
        """
        Busca el acumulado de los pagos, considerando los netos gravados de las facturas que se pagaron
        """
        accumulated = 0
        for payment in self:
            payment_move_lines = payment.env['account.move.line'].search([('payment_id', '=', payment.id)])
            # El account.partial.reconcile une las invoices con el pago y tiene el importe de cuanto se imputo
            print (payment_move_lines.mapped('name'))
            for payment_move_line in payment_move_lines.filtered(lambda x: x.debit > 0):
                print (payment_move_line.name, payment_move_line.move_id.currency_rate, payment_move_line.move_id.current_currency_rate)
                accumulated += payment_move_line.debit
                print ("1", accumulated)
                for credit_reconcile in payment_move_line.matched_credit_ids:
                    invoice = credit_reconcile.credit_move_id.move_id
                    # Para facturas A retenemos importes gravados o exentos, si no, el total.
                    if invoice and invoice.voucher_type_id.denomination_id.vat_discriminated:
                        # Sacamos la diferencia entre los impuestos y la factura,
                        # ya que solo se retiene sobre el neto gravado
                        if invoice.amount_to_tax or invoice.amount_exempt:
                            print ("__", credit_reconcile.amount, invoice.amount_total, invoice.amount_to_tax, invoice.amount_exempt)
                            invoice_tax = invoice.amount_total / (invoice.amount_to_tax + invoice.amount_exempt)

                            print ("___", invoice_tax, invoice.currency_rate, payment.currency_rate)
                            #currency rate from payment not invoice
                            #invoice_tax = invoice_tax * invoice.currency_rate / payment.currency_rate

                        else:
                            invoice_tax = None
                        # En ese caso le restamos al importe pagado la parte de impuestos, si no, no se retiene
                        accumulated -= credit_reconcile.amount - (credit_reconcile.amount / invoice_tax) if invoice_tax \
                            else credit_reconcile.amount
                    else:
                        accumulated -= credit_reconcile.amount
                print ("2", accumulated)

        return accumulated

class RetentionRetention(models.Model):
    _inherit = 'retention.retention'

    def calculate_profit_retention(self, partner, amount, payment=None, rate=None):
        """
        Devuelve el valor de la retencion de ganancia que se le deberia a efectuar al partner pagandole esa cantidad
        :param partner: res.partner del cual se buscara el acumulado y la actividad
        :param amount: Importe que se pagara (neto gravado).
        :param payment: Se utilizará la fecha que se utilizará como parametro para la busqueda del acumulado
        """
        ywt_moogah_profit_scales_tables_obj = self.env['ywt.moogah.profit.scales.tables']
        retention_rule = self.get_profit_retention_rule(partner)
        if not retention_rule:
            return 0, 0
        date = fields.Date.from_string(payment.date if payment else None) or fields.Date.today()
        accumulated_payments = self.env['account.payment'].search([
            ('payment_type', '=', 'outbound'),
            ('partner_id', '=', partner.id),
            ('state', 'not in', ['draft', 'cancel']),
            ('date', '>=', fields.Date.to_string(date.replace(day=1))),
            ('date', '<', fields.Date.to_string(date.replace(day=1) + relativedelta(months=1))),
            ('company_id', '=', self.company_id.id or self.env.company.id)
        ])
        accumulated_amount = accumulated_payments.get_accumulated_amount()
        retention_profit = tribute.Tribute.get_tribute(self.type)
        if partner.income_wh_registration == '1':
            if not retention_rule.scale_id:
                retention_profit.activity = tribute.Activity(retention_rule.not_applicable_minimum, retention_rule.minimum_tax, retention_rule.percentage)
            if retention_rule.scale_id:

                usable_value = accumulated_amount + amount - retention_rule.not_applicable_minimum
                _logger.info(str(usable_value))
                _logger.info(str(accumulated_amount))
                _logger.info(str(amount))
                _logger.info(str(retention_rule.not_applicable_minimum))

                scales_table_list = []
                scales_tables_ids = retention_rule.scale_id.line_ids #ywt_moogah_profit_scales_tables_obj.search([])
                for scales_tables_id in scales_tables_ids:
                    if usable_value >= scales_tables_id.from_dollar and usable_value <= scales_tables_id.to_dollar:
                        scales_table_list.append(scales_tables_id.id)
                ywt_moogah_profit_scales_tables_id = ywt_moogah_profit_scales_tables_obj.search([('id', 'in', scales_table_list)], limit=1)
                if ywt_moogah_profit_scales_tables_id:
                    base_am = usable_value - ywt_moogah_profit_scales_tables_id.value_over_dollar

                    v = base_am * ywt_moogah_profit_scales_tables_id.plus_percentage / 100
                    _logger.info(str(base_am))
                    _logger.info(str(ywt_moogah_profit_scales_tables_id.plus_percentage))

                    prev_ret_amount = 0
                    for paym in accumulated_payments:
                        for ret in paym.retention_ids.filtered(lambda x: x.type == 'profit'):
                            prev_ret_amount += ret.amount
                    _logger.info(str(prev_ret_amount))

                    retention_profit.activity = tribute.Activity(
                        retention_rule.not_applicable_minimum, retention_rule.minimum_tax, retention_rule.percentage
                    )
                    return retention_profit.calculate_value(accumulated_amount, amount)[0], round(v-prev_ret_amount+ywt_moogah_profit_scales_tables_id.plus_dollar, 2)
                else:
                    return 0, 0
        if partner.income_wh_registration == '2':
            if not retention_rule.scale_id:
                retention_profit.activity = tribute.Activity(retention_rule.not_applicable_minimum, retention_rule.minimum_tax, retention_rule.not_registered_percentage)
    
        return retention_profit.calculate_value(accumulated_amount, amount)


class RetentionRetentionRule(models.Model):
    _inherit = 'retention.retention.rule'
    
    # use_scale = fields.Boolean(string='Use Scale', default=False)
    not_registered_percentage = fields.Float(string='No Registrado %',default=0.00)
    scale_id = fields.Many2one('ywt.moogah.profit.scales.tables.header',string="Escala")
    
    @api.constrains('not_registered_percentage')
    def _check_not_registered_percentage(self):
        for record_id in self:
            if record_id.not_registered_percentage < 0:
                 raise UserError("No esta permitido ingresar % un Valor Negativo")

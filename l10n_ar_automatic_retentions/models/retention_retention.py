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
from odoo.exceptions import ValidationError
from . import payment as payment_accumulated
from datetime import date
from l10n_ar_api.documents import tribute

RETENTIONS_CALCULATION_FUNCTIONS = {
    'profit': 'calculate_profit_retention',
    'gross_income': 'calculate_gross_income_retention',
    'other': 'calculate_other_retention',
}


class RetentionRetention(models.Model):

    _inherit = 'retention.retention'

    def get_profit_retention_rule(self, partner_id, limit_date=fields.Date.today()):
        """
        Busca la regla de retencion de ganancia para la actividad del partner
        :param partner_id: res.partner del cual se usará la actividad configurada
        :return: retention.retention.rule de la retencion para esa actividad
        """
        retention_partner = partner_id.retention_partner_rule_ids.filtered(lambda x: x.retention_id == self)
        if not retention_partner:
            raise ValidationError("El partner no tiene configurada la actividad para retener ganancias")
        if retention_partner.is_excepted(limit_date):
            return False

        retention_rule = self.retention_rule_ids.filtered(lambda x: x.activity_id == retention_partner.activity_id)
        if not retention_rule:
            raise ValidationError(
                "No se encontro una regla configurada en la retencion con la actividad del partner\n"
                "Por favor, configure una desde las reglas de la retencion"
            )

        return retention_rule

    def calculate_profit_retention(self, partner, amount, payment=None, rate=None, limit_date=fields.Date.today()):
        """
        Devuelve el valor de la retencion de ganancia que se le deberia a efectuar al partner pagandole esa cantidad
        :param partner: res.partner del cual se buscara el acumulado y la actividad
        :param amount: Importe que se pagara (neto gravado).
        :param payment: Se utilizará la fecha que se utilizará como parametro para la busqueda del acumulado
        """
        retention_rule = self.get_profit_retention_rule(partner, limit_date=limit_date)
        if not retention_rule:
            return 0, 0
        accumulated_payments = payment_accumulated.get_accumulated_payments(
            self, partner, fields.Date.from_string(payment.date if payment else None) or date.today()
        )
        accumulated_amount = accumulated_payments.get_accumulated_amount()
        retention_profit = tribute.Tribute.get_tribute(self.type)
        retention_profit.activity = tribute.Activity(
            retention_rule.not_applicable_minimum, retention_rule.minimum_tax, retention_rule.percentage
        )

        return retention_profit.calculate_value(accumulated_amount, amount)

    def calculate_gross_income_retention(self, partner, amount, payment=None, rate=None, limit_date=fields.Date.today()):
        """
        Devuelve el valor de la retencion de ganancia que se le deberia a efectuar al partner pagandole esa cantidad
        :param partner: res.partner del cual se buscara el porcentaje a retener
        :param amount: Importe que se pagara (neto gravado).
        :param payment: Pago del cual se tomará la jurisdicción.
        """
        retention_gross_income = tribute.Tribute.get_tribute(self.type)
        values = self.get_gross_income_values(partner, limit_date=limit_date)
        retention_gross_income.percentage = values[0]
        retention_gross_income.minimum_no_aplicable = values[1]
        retention_gross_income.minimum_tax = values[2]

        return retention_gross_income.calculate_value(amount)

    def get_gross_income_values(self, partner, limit_date=fields.Date.today()):
        """
        Busca el porcentaje y minimo no aplicableque se debe utilizar para retener,
        el importe es el del partner en el caso que exista, si no, el general.
        :param partner: res.partner del cual se buscara el porcentaje a retener
        :return:
        """
        retention_partner = partner.retention_partner_rule_ids.filtered(lambda x: x.retention_id == self)
        if retention_partner.is_excepted(limit_date):
            return 0, 0, 0
        retention = self.env['retention.retention.rule'].search([
            ('retention_id', '=', self.id)],
            limit=1
        )
        if not retention:
            raise ValidationError(
                "No se encontro una regla para retener ingresos brutos de {}".format(self.state_id.name)
            )
        percentage = retention_partner.percentage if retention_partner else retention.percentage
        minimum_no_aplicable = retention.not_applicable_minimum
        minimum_tax = retention.minimum_tax

        return percentage, minimum_no_aplicable, minimum_tax
    
    def calculate_other_retention(self, partner, amount, payment=None, rate=None, limit_date=fields.Date.today()):
        retention_partner = partner.retention_partner_rule_ids.filtered(
            lambda x: x.retention_id == self and not x.is_excepted(limit_date)
        )
        if not retention_partner:
            return amount, 0
        return amount, amount * retention_partner.percentage / 100

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

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

from odoo import models, fields
from dateutil.relativedelta import relativedelta


WEEKDAYS_DELTA = {
    5: 2,
    6: 1,
}


class CashFlowConfiguration(models.Model):
    _inherit = 'cash.flow.configuration'

    credit_card_coupon = fields.Boolean(
        string='Cupones'
    )

    def get_values(self, date_from, date_to, cash_flow_id):
        """Genera las lineas segun la configuracion"""
        values = super(CashFlowConfiguration, self).get_values(date_from, date_to, cash_flow_id)
        # Cupones
        if self.credit_card_coupon:
            coupons = self.env['credit.card.coupon'].search([
                ('state', '=', 'closed'),
                ('estimated_amount', '>', 0),
                ('estimated_date', '!=', False),
            ])
            values += self._get_coupon_values(date_from, date_to, coupons, cash_flow_id)
        return values

    # Cupones
    @staticmethod
    def _get_coupon_values(date_from, date_to, credit_card_coupons, cash_flow_id):
        """Se obtienen los cupones para el rango de fechas
        :param date_from: Fecha de inicio
        :param date_to: Fecha de fin
        :return: Lista de cupones
        """
        coupons = []
        # Se buscan los cupones y se contempla casos de fin de semana
        for coupon in credit_card_coupons:
            coupon_date = coupon.estimated_date
            # Se saltean dias basado a si es sabado o domingo
            coupon_date += relativedelta(days=WEEKDAYS_DELTA.get(coupon_date.weekday(), 0))
            # Se agrega clearing
            coupon_date += relativedelta(days=1)
            # Se vuelven saltear dias basado a si es sabado o domingo luego de sumado el clearing
            coupon_date += relativedelta(days=WEEKDAYS_DELTA.get(coupon_date.weekday(), 0))

            # Seteo la fecha en el cupon
            coupon_date = coupon_date if coupon_date >= date_from else date_from
            # Si la fecha coincide con el rango se agrega el cupon
            if date_from <= coupon_date <= date_to:
                reference = 'Cupón N° {}'.format(coupon.name)
                coupons.append({
                    'reference': reference,
                    'credit': 0,
                    'debit': coupon.estimated_amount,
                    'date': coupon_date,
                    'balance': coupon.estimated_amount,
                    'cash_flow_id': cash_flow_id
                })
        return coupons

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

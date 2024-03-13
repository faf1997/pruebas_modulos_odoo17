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


class SaleSuscriptionPriceAdjustmentWizard(models.TransientModel):
    _name = 'sale.subscription.price.adjustment.wizard'

    adjustment_percentage = fields.Float(
        '% Ajuste',
        required=True
    )
    date_adjustment = fields.Date(
        'Fecha de ajuste',
        default=fields.Date.today(),
        help='Fecha que se tomará para determinar si corresponde ajustar o no',
        required=True
    )
    end_date_adjustment = fields.Date(
        'No actualizar precios hasta:',
        help='Fecha hasta la cual se mantendrá el nuevo precio',
    )

    def adjust_price(self):
        subscriptions = self.env['sale.subscription'].browse(self.env.context.get('active_ids'))
        if not self.adjustment_percentage:
            raise ValidationError("El ajuste no puede ser del 0%.")
        # Solo se ajustarán las suscripciones que la fecha de ajuste sea menor al día del ajuste.
        for subscription in subscriptions.filtered(
                lambda x: not x.date_to_adjust_price or x.date_to_adjust_price <= self.date_adjustment
        ):
            for line in subscription.recurring_invoice_line_ids:
                line.price_unit += line.price_unit * self.adjustment_percentage / 100
            subscription.message_post(body="Precio actualizado por ajuste: {}%".format(self.adjustment_percentage))
            if self.end_date_adjustment:
                subscription.date_to_adjust_price = self.end_date_adjustment

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

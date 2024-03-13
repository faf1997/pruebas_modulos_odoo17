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
from datetime import timedelta


class CreditCardCoupon(models.Model):
    _name = 'credit.card.coupon'
    _inherit = 'credit.card.summary'
    _description = 'Cupón de tarjeta de crédito'

    state = fields.Selection(
        [('draft', "Borrador"), 
         ('approved', "Aprobado"),
         ('closed', "Cerrado"),
         ],
        "Estado", 
        default='draft'
    )
    date = fields.Date("Fecha")
    presentation_date = fields.Date("Fecha de presentación")
    estimated_date = fields.Date("Fecha estimada")
    closure_date = fields.Date("Fecha de cierre")
    estimated_amount = fields.Float("Monto estimado")
    scan = fields.Binary(string="Escaneo")
    user_id = fields.Many2one('res.users', "Vendedor")

    def generate_summary(self, line):
        """ Si el pago es de proveedor el cupón tiene que ser negativo """
        payment_type = line.payment_id.payment_type
        sign = -1 if payment_type == 'outbound' else 1
        return self.create({
            'name': line.name,
            'amount': sign * line.amount,
            'credit_card_id': line.credit_card_id.id,
            'payment_plan_id': line.payment_plan_id.id,
            'payment_id': line.payment_id.id,
            'date': line.payment_id.date,
            'presentation_date': line.payment_id.date,
            'user_id': self.env.user.id,
            'state': 'approved'
        })

    def get_estimated_amount(self):
        return self.amount * self.payment_plan_id.credit_percentage / 100.0

    def get_estimated_date(self, closure_date):
        holidays = self.env['credit.card.holiday'].search([]).mapped('date')
        date = closure_date
        i = 0
        while i < self.payment_plan_id.credit_days:
            date += timedelta(days=1)
            if date.weekday() < 5 and date not in holidays:
                i += 1
        return date

    def close(self, closure_date):
        self.update({
            'state': 'closed',
            'closure_date': closure_date,
            'estimated_date': self.get_estimated_date(closure_date),
            'estimated_amount': self.get_estimated_amount(),
        })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

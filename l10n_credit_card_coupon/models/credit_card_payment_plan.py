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


class CreditCardPaymentPlan(models.Model):
    _inherit = 'credit.card.payment.plan'

    credit_days = fields.Integer("Días de acreditación")
    credit_percentage = fields.Float("Porcentaje estimado de acreditación", digits=(2, 6))

    @api.constrains('credit_percentage')
    def check_credit_percentage(self):
        if any(r.credit_percentage < 0 or r.credit_percentage > 100 for r in self):
            raise ValidationError("Porcentaje estimado de acreditación inválido")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

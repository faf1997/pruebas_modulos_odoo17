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


class ResCurrencyRateCashFlow(models.Model):
    _name = 'res.currency.rate.cash.flow'
    _order = "name desc"

    name = fields.Date(
        string='Fecha',
        default=lambda *a: fields.Date.today() + ' 00:00:00',
        required=True
    )
    rate = fields.Float(
        string='Tasa futura',
        digits=(12, 6)
    )
    currency_id = fields.Many2one(
        comodel_name='res.currency',
        string='Moneda',
        readonly=True
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Compañia',
        default=lambda self: self.env.user._get_company()
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

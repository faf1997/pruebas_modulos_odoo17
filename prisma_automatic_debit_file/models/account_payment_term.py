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


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    is_automatic_debit = fields.Boolean(string='Es débito automático')
    
    card_type = fields.Selection(
        [
            ('DEBLIQC', 'Visa Crédito'),
            ('DEBLIQD', 'Visa Débito'),
            ('DEBLIMC', 'MasterCard Crédito')
        ], 'Tipo de tarjeta'
    )

    @api.onchange('is_automatic_debit')
    def onchange_automatic_debit(self):
        self.card_type = False

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
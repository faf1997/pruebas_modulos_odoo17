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

from odoo import models, api


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def should_generate_retentions(self):
        self.ensure_one()
        return self.payment_type == 'outbound' and self.partner_type == 'supplier'

    @api.onchange('journal_id')
    def onchange_partner_calculate_retentions(self):
        if self.should_generate_retentions() and self.env.context.get('active_model') == 'account.move':
            payment = self.env['account.payment'].new(self._create_payment_vals_from_wizard())
            payment.create_retentions()
            self.retention_ids = [(5, 0, 0)]
            retentions = []
            for retention in payment.retention_ids:
                retentions.append((0, 0, {
                    'base': retention.base,
                    'aliquot': retention.aliquot,
                    'date': retention.date,
                    'retention_id': retention.retention_id.id,
                    'certificate_no': retention.certificate_no,
                    'type': retention.type,
                    'jurisdiction': retention.jurisdiction,
                    'activity_id': retention.activity_id.id,
                    'amount': retention.amount,
                    'company_id': retention.company_id.id,
                    'journal_id': retention.journal_id.id,
                    'name': retention.name,
                    'payment_currency_amount': retention.payment_currency_amount,
                    'rate': retention.rate,
                }))
            self.update({'retention_ids': retentions})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

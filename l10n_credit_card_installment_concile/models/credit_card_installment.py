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


class CreditCardInstallment(models.Model):
    _inherit = 'credit.card.installment'

    reconciled = fields.Boolean('Conciliado', readonly=True)
    concile_ids = fields.Many2many(
        'credit.card.installment.concile',
        'credit_card_installment_concile_rel',
        'installment_id',
        'concile_id',
        string='conciliaciones'
    )

    @api.constrains('concile_ids')
    def constraint_multiple_conciliations(self):
        for installment in self:
            if len(installment.concile_ids) > 1:
                raise ValidationError("Una cuota no puede pertenecer a múltiples conciliaciones.")

    def reconcile(self):
        self.write({'reconciled': True})

    def cancel_reconcile(self):
        self.write({'reconciled': False})

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

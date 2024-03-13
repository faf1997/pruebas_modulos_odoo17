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


class WizardCurrencyExchange(models.TransientModel):
    _name = 'wizard.currency.exchange'
    _description = 'Cambiar moneda'

    def _get_default_moves(self):
        return self.env['account.move'].browse(self.env.context.get('active_ids'))

    move_id = fields.Many2one('account.move', default=_get_default_moves)
    current_currency = fields.Many2one('res.currency', string="Moneda actual", related="move_id.currency_id")
    new_currency = fields.Many2one('res.currency', string="Moneda nueva")
    exchange_rate = fields.Float(string="Tasa de cambio")


    def action_calculate_new_prices(self):
        invoice = self.move_id
        if self.new_currency == self.env.company.currency_id:
            currency_rate = 0.0
        elif self.new_currency != self.env.company.currency_id != self.current_currency:
            currency_rate = 0.0
        else:
            currency_rate = self.exchange_rate
        invoice.with_context(check_move_validity=False).write({'currency_id': self.new_currency, 'currency_rate': currency_rate})
        line_ids = invoice.invoice_line_ids
        for line in line_ids:
            price_unit = line.price_unit * self.exchange_rate
            line.with_context(check_move_validity=False).write({'price_unit': price_unit})

        # Estaria bueno ejecutar este metodo que ejecuta los onchange del campo que se le pasa
        # pero no funciona :(
        # asi evitamos dependencias innecesarias
        # for method in invoice._onchange_methods.get('price_unit',  ()):
        #     getattr(invoice, method.__name__)

        invoice.with_context(check_move_validity=False)._onchange_currency()
        invoice.with_context(check_move_validity=False).onchange_invoice_line_perception()
        invoice.with_context(check_move_validity=False)._recompute_dynamic_lines(True, True)


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

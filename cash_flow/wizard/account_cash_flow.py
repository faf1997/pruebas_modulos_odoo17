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
from odoo.exceptions import ValidationError
from datetime import date
from dateutil.relativedelta import relativedelta


class AccountCashFlow(models.TransientModel):
    _name = 'account.cash.flow'

    name = fields.Char(
        string='Nombre'
    )
    date_start = fields.Date(
        string='Desde',
        required=True,
        default=fields.Date.context_today
    )
    date_stop = fields.Date(
        string='Hasta',
        required=True
    )
    configuration_id = fields.Many2one(
        comodel_name='cash.flow.configuration',
        ondelete='cascade',
        string='Configuracion',
        required=True,
    )
    cash_flow_line_ids = fields.One2many(
        comodel_name='account.cash.flow.line',
        inverse_name='cash_flow_id',
        string='Lineas'
    )

    @api.onchange('configuration_id')
    def onchange_configuration(self):
        """ Seteo la fecha hasta segun la configuracion """
        self.date_stop = False
        if self.configuration_id:
            self.date_stop = date.today() + relativedelta(days=self.configuration_id.qty_days)

    @api.constrains('date_start', 'date_stop')
    def check_date(self):
        """Valido el rango de fechas"""
        if self.date_start > self.date_stop:
            raise ValidationError('La fecha desde no puede ser mayor a la fecha hasta')

    def generate_lines(self, cash_flow_id):
        """Se genera la informacion del cashflow segun las fechas y la configuraciones"""
        # Se generan las lineas segun las configuraciones
        self.configuration_id._compute(self.date_start, self.date_stop, cash_flow_id)
        # Calculamos el acumulado de cada linea
        self._set_accumulated(cash_flow_id)

    def _set_accumulated(self, cash_flow_id):
        """Se calcula el acumulado en cada linea segun el debito y credito"""
        lines = self.env['account.cash.flow.line'].search(
            [('cash_flow_id', '=', cash_flow_id)]
        ).sorted(key=lambda l: l.date)
        accumulated = 0
        for line in lines:
            accumulated += line.debit - line.credit
            line.accumulated = accumulated

    def compute_cash_flow(self):
        """Crea nuevas lineas y las devuelve muestra en las vistas"""
        # Genero los registros
        self.generate_lines(self.id)
        # Devuelvo la vista
        return {
            'name': 'Cash Flow',
            'views': [[False, "tree"], [False, "graph"], [False, "pivot"]],
            'domain': [("cash_flow_id", '=', self.id)],
            'res_model': 'account.cash.flow.line',
            'type': 'ir.actions.act_window',
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

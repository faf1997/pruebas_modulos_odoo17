# -*- coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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


class AccountCashFlowLine(models.TransientModel):
    _name = 'account.cash.flow.line'
    _order = 'date, id asc'

    date = fields.Date(
        string='Fecha',
        required=True
    )
    reference = fields.Char(
        string='Referencia'
    )
    debit = fields.Float(
        string='Debito'
    )
    credit = fields.Float(
        string='Credito'
    )
    balance = fields.Float(
        string='Balance',
    )
    accumulated = fields.Float(
        string='Acumulado'
    )
    cash_flow_id = fields.Many2one(
        comodel_name='account.cash.flow',
        string='Cash flow'
    )

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """
        Redefino un metodo base para que que busque el acumulado del movimiento mas actual del periodo
        """
        res = super(AccountCashFlowLine, self).read_group(domain,
                                                          fields,
                                                          groupby,
                                                          offset=offset,
                                                          limit=limit,
                                                          orderby=orderby,
                                                          lazy=lazy
                                                          )
        if 'accumulated' in fields:
            for group in res:
                if '__domain' in group:
                    lines = self.search(group['__domain'])
                    if lines:
                        accumulated = lines.sorted(lambda l: (l.id, l.date), reverse=True)[0].accumulated
                        group['accumulated'] = accumulated
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

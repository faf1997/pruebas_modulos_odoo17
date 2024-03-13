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


class ResPartner(models.Model):

    _inherit = 'res.partner'

    perception_partner_rule_ids = fields.One2many(
        comodel_name='perception.partner.rule',
        inverse_name='partner_id',
        string="Alicuotas de percepciones",
        domain=lambda l: [('company_id', 'in', l.env.companies.ids)],
    )

    @api.onchange('parent_id')
    def onchange_customer_parent_id(self):
        self.perception_partner_rule_ids = [(2, rule.id) for rule in self.perception_partner_rule_ids]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

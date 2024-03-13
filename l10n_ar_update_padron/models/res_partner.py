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

from odoo import models, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.onchange('vat')
    def onchange_vat(self):
        self.update_rules()

    def update_rules(self):
        """ Actualiza las reglas de retencion y percepcion"""
        # Elimino las alicuotas del partner para la percepcion y retencion a cargar
        for partner in self:
            partner.perception_partner_rule_ids = [(2, rule.id) for rule in self.perception_partner_rule_ids.filtered(lambda l: l.perception_id.type == 'gross_income')]
            partner.retention_partner_rule_ids = [(2, rule.id) for rule in self.retention_partner_rule_ids.filtered(lambda l: l.retention_id.type == 'gross_income')]
            # Si tiene documento genero las reglas
            if partner.vat:
                rules = partner.get_rule_values()
                if rules:
                    print(rules)
                    partner.perception_partner_rule_ids = rules[0]
                    partner.retention_partner_rule_ids = rules[1]

    def get_rule_values(self):
        """ Hook para agregar reglas de retencon en cada padrón """
        self.ensure_one()
        return [[], []]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

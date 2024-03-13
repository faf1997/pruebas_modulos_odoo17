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

from odoo import models
from datetime import datetime


class ResPartner(models.Model):
    _inherit = 'res.partner'

    def get_rule_values(self):
        """ Actualizamos las reglas de retenciones y percepciones de Tucumán en el partner """
        rules = super(ResPartner, self).get_rule_values()

        padron_vat = self.env['padron.iibb.tucuman'].get_padron_line(self.vat)

        if padron_vat:
            # Obtenemos las reglas de percepción y retención
            retention_partner_rule = {
                'percentage': float(padron_vat.aliquot),
                'date_from': datetime.strptime(padron_vat.date_from, '%Y%m%d').date(),
                'date_to': datetime.strptime(padron_vat.date_to, '%Y%m%d').date(),
            }
            perception_partner_rule = dict(retention_partner_rule)
            perception_partner_rule['perception_id'] = self.env['perception.perception'].get_tucuman_perception().id
            retention_partner_rule['retention_id'] = self.env['retention.retention'].get_tucuman_retention().id
            rules[0].append((0, 0, perception_partner_rule))
            rules[1].append((0, 0, retention_partner_rule))

        return rules

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

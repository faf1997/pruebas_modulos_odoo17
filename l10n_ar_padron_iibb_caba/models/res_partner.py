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

    def get_partner_rule_iibb_caba_dict(self, percentage, padron_vat, perception=False, retention=False):
        """ Generamos un diccionario con el rango de fechas y porcentaje para retención o percepción"""
        res = {
            'percentage': percentage,
            'date_from': datetime.strptime(padron_vat.date_from, '%d%m%Y').date(),
            'date_to': datetime.strptime(padron_vat.date_to, '%d%m%Y').date(),
        }
        if perception:
            res['perception_id'] = self.env['perception.perception'].get_caba_perception().id
        if retention:
            res['retention_id'] = self.env['retention.retention'].get_caba_retention().id
        return res

    def get_rule_values(self):
        rules = super(ResPartner, self).get_rule_values()

        # Si se encuentra, la alícuota debería ser única
        padron_vat = self.env['padron.iibb.caba'].get_padron_line(self.vat)

        if padron_vat:
            # Convertimos el porcentaje
            perception_percentage = float(
                padron_vat.perception_aliquot[0] + '.' + padron_vat.perception_aliquot[2:]
            )
            retention_percentage = float(
                padron_vat.retention_aliquot[0] + '.' + padron_vat.retention_aliquot[2:]
            )
            # Obtenemos las reglas de percepción y retención
            perception_partner_rule = self.get_partner_rule_iibb_caba_dict(
                perception_percentage,
                padron_vat,
                perception=True
            )
            retention_partner_rule = self.get_partner_rule_iibb_caba_dict(
                retention_percentage,
                padron_vat,
                retention=True
            )
            rules[0].append((0, 0, perception_partner_rule))
            rules[1].append((0, 0, retention_partner_rule))

        return rules

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

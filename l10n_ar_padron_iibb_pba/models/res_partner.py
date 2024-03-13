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

from odoo import models
from datetime import datetime


class ResPartner(models.Model):

    _inherit = 'res.partner'

    def get_partner_rule_iibb_pba_perception_dict(self):
        padron_iibb_pba_proxy = self.env['padron.iibb.pba']
        for partner in self:
            padron_line = padron_iibb_pba_proxy.get_perception_padron_line(partner.vat)
            if padron_line:
                pba_perception = self.env['perception.perception'].get_iibb_pba_perception()
                return {
                    'percentage': float(padron_line.aliquot[0] + '.' + padron_line.aliquot[2:]),
                    'date_from': datetime.strptime(padron_line.validity_date_since, '%d%m%Y').date(),
                    'date_to': datetime.strptime(padron_line.validity_date_to, '%d%m%Y').date(),
                    'perception_id': pba_perception.id,
                    'company_id': pba_perception.company_id.id or self.env.company.id
                }

    def get_partner_rule_iibb_pba_retention_dict(self):
        padron_iibb_pba_proxy = self.env['padron.iibb.pba']
        for partner in self:
            padron_line = padron_iibb_pba_proxy.get_retention_padron_line(partner.vat)
            if padron_line:
                pba_retention = self.env['retention.retention'].get_iibb_pba_retention()
                return {
                    'percentage': float(padron_line.aliquot[0] + '.' + padron_line.aliquot[2:]),
                    'date_from': datetime.strptime(padron_line.validity_date_since, '%d%m%Y').date(),
                    'date_to': datetime.strptime(padron_line.validity_date_to, '%d%m%Y').date(),
                    'retention_id': pba_retention.id,
                    'company_id': pba_retention.company_id.id or self.env.company.id
                }

    def get_rule_values(self):
        rules = super(ResPartner, self).get_rule_values()

        # Obtenemos las reglas de percepcion y retencion
        perception_partner_rule = self.get_partner_rule_iibb_pba_perception_dict()
        retention_partner_rule = self.get_partner_rule_iibb_pba_retention_dict()
        if perception_partner_rule:
            rules[0].append((0, 0, perception_partner_rule))
        if retention_partner_rule:
            rules[1].append((0, 0, retention_partner_rule))

        return rules

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

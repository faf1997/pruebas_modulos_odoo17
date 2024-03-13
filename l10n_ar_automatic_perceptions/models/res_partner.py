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
from odoo.exceptions import ValidationError


class ResPartner(models.Model):  # Se encarga de buscar la alicuota
    _inherit = 'res.partner'

    def get_perceptions_values(self, state, company, limit_date=fields.Date.today()):
        """ PERCEPCIONES - Art 318, 321 y 407 DISP 1/ENERO/2004 """
        self.ensure_one()
        vals = []
        perceptions = company.sudo().perception_ids

        for company_perception in perceptions:
            # Cuando está inscripto en padron (Con porcentaje en el partner) se debe percibir ese porcentaje.
            if company_perception.mapped('perception_id') in self.perception_partner_rule_ids.mapped('perception_id'):
                perception_partner = self.sudo().perception_partner_rule_ids.filtered(
                    lambda x: x.perception_id == company_perception.perception_id
                )
                if perception_partner and perception_partner.is_excepted(limit_date):
                    continue
                vals.append({perception_partner.perception_id: perception_partner.percentage})

            # Si es consumidor final no se le percibe porque se entiende que es un bien de uso.
            elif self.property_account_position_id and\
                    self.property_account_position_id.ar_fiscal_position_id != self.env.ref('l10n_ar.ar_fiscal_position_cf'):
                if not state:
                    raise ValidationError("No se pudo realizar el cálculo de la percepción porque "
                                          "falta la carga de la jurisdicción de entrega.")

                # En el caso que no esté inscripto se percibe únicamente
                # si se entrega en la jurisdicción de la percepción.
                elif company_perception.perception_id.state_id == state:
                    percentage = company_perception.perception_id.perception_rule_ids[0].percentage\
                        if company_perception.perception_id.perception_rule_ids else 0.0
                    vals.append({company_perception.perception_id: percentage})

        return vals

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

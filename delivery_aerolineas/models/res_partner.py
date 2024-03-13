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


class ResPartner(models.Model):

    _inherit = 'res.partner'

    def _get_aerolineas_shipper_data(self, company_id, carrier_id):
        return {
            "type": "Shipper",
            "primaryId": carrier_id.primaryId[:36],
            "account": carrier_id.account[:120],
            "name": (self.name or '')[:120],
            "postCode": (self.zip or '')[:15],
            "street": (self.street or '')[:100],
            "city": (self.city or '')[:60],
            "countryId": (company_id.country_id.code or '')[:2],
            "phoneNumber": (self.phone or '')[:16],
            "taxIdentificationNumbers": [
                {
                    "Type": self.partner_document_type_id.name or '',
                    "Value": (self.vat or '')[:20],
                }
            ],
        }

    def _get_aerolineas_consignee_data(self, company_id):
        return {
            "type": "Consignee",
            "primaryId": '', 
            "account": '',
            "name": (self.name or '')[:120],
            "postCode": (self.zip or '')[:15],
            "street": (self.street or '')[:100],
            "city": (self.city or '')[:60],
            "countryId": (company_id.country_id.code or '')[:2],
            "phoneNumber": (self.phone or '')[:16],
            "taxIdentificationNumbers": [
                {
                    "Type": self.partner_document_type_id.name or '',
                    "Value": (self.vat or '')[:20],
                }
            ],
        }
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

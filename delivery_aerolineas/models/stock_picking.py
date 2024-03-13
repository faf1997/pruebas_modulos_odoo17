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
from itertools import groupby
from datetime import datetime

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

class StockPicking(models.Model):

    _inherit = 'stock.picking'
    
    def _get_aerolineas_data(self):
        self.ensure_one()
        data = {
            'reference': (self.move_ids_without_package.sale_line_id.order_id.name or self.name)[:35], # Este campo hace referencia a la venta o en su defecto al remito
            'issueDate': datetime.now().strftime(DATE_FORMAT),
            'packages': self._get_aerolineas_packages(),
        }
        return data
    
    def _get_aerolineas_packages(self):
        data = []
        line_ids = self.move_line_ids_without_package.filtered(lambda l: l.product_id.aerolineas_product and l.qty_done)
        # Agrupo por el paquete de destino
        participants = self._get_participants()
        for k, l in groupby(line_ids, key=lambda l: l.result_package_id.id or 0):
            # Si hay un paquete de destino entonces registro el paquete en una linea
            # Si no hay un paquete de destino entonces registro cada producto individualmente
            items = list(l)
            if k:
                pack_id = self.env['stock.quant.package'].browse(k)
                data.append({
                    "reference": pack_id.name[:35],
                    "commodityType": self.carrier_id.commodityType[:60],
                    "serviceType": self.carrier_id.service_type,
                    "paymentMode": self.carrier_id.paymentMode[:2],
                    "packageDescription": self.get_aerolineas_pack_description(line_ids, pack_id)[:100],
                    "totalPackages": 1,
                    "totalPieces": 1,
                    "grossVolumeUnitMeasure": "CMQ", # Esto indica que la unidad de medida es en centimetros
                    "totalGrossWeight": pack_id.shipping_weight,
                    "grossWeightUnitMeasure": "KG",
                    "declaredValue": 0,
                    "dimensions": [{
                        "pieces": 1,
                        "height": pack_id.package_type_id.height/10 or 1,
                        "width": pack_id.package_type_id.width/10 or 1,
                        "length": pack_id.package_type_id.packaging_length/10 or 1,
                        "grossWeight": pack_id.shipping_weight,
                    }],
                    "participants": participants,
                })
            else:
                for p in items:
                    # Por cada unidad del producto entregada agrego una linea
                    for i in range(int(p.qty_done)):
                         data.append({
                            "reference": ((p.product_id.default_code or f'{p.product_id.name}')+ f'-{i}')[:35],# Se le agrega el i porque la referencia tiene que ser unica
                            "commodityType": self.carrier_id.commodityType[:60],
                            "serviceType": self.carrier_id.service_type,
                            "paymentMode": self.carrier_id.paymentMode[:2],
                            "packageDescription": (p.move_id.sale_line_id.name or p.product_id.name)[:100],
                            "totalPackages": 1,
                            "totalPieces": 1,
                            "grossVolumeUnitMeasure": "CMQ", # Esto indica que la unidad de medida es en centimetros
                            "totalGrossWeight": p.product_id.weight or 0,
                            "grossWeightUnitMeasure": "KG",
                            "declaredValue": 0,
                            "dimensions": [{
                                "pieces": 1,
                                "height": 1,
                                "width": 1,
                                "length": 1,
                                "grossWeight": p.product_id.weight or 0,
                            }],
                            "participants": participants,
                        })

        return data

    def _get_participants(self):
        return [
            self.carrier_id.shipper_contact._get_aerolineas_shipper_data(self.company_id, self.carrier_id),
            self.partner_id._get_aerolineas_consignee_data(self.company_id),
        ]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

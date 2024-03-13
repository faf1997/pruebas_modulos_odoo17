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


class StockPicking(models.Model):

    _inherit = 'stock.picking'
    
    def _get_epsa_data(self):
        self.ensure_one()
        data = {
            'envio_segurizado': 0,
            'fragil': 1,
            'internacional': 0,
            'valor_declarado': self.get_valor_declarado(),
            'isInversa': 0,
            'pago_en': 'ORIGEN',
            'tipo_operacion': 'ENTREGA',
            'is_urgente': 0,
            'comprador': self._get_epsa_buyer_data(),
            'productos': self._get_epsa_product_data(),
        }

        return data

    def _get_epsa_buyer_data(self):
        return {
            "destinatario": self.partner_id.name or '',
            "calle": self.partner_id.street or '',
            "altura": self.partner_id.street2 or '',
            "localidad": self.partner_id.city or '',
            "provincia": self.partner_id.state_id.name or '',
            "cp": self.partner_id.zip or '',
            'email': self.partner_id.email or '',
        }
    
    def _get_epsa_product_data(self):
        data = []
        # Filtro las lineas con cnatidades a entregar mayores que cero
        line_ids = self.move_line_ids_without_package.filtered(lambda l: l.qty_done)
        # Agrupo por el paquete de destino
        for k, l in groupby(line_ids, key=lambda l: l.result_package_id.id or 0):
            # Si hay un paquete de destino entonces registro el paquete en una linea
            # Si no hay un paquete de destino entonces registro cada producto individualmente
            items = list(l)
            if k:
                pack_id = self.env['stock.quant.package'].browse(k)
                data.append({
                "bultos": 1,
                "peso": pack_id.shipping_weight,
                "descripcion": pack_id.name,
                "dimensiones": {
                    "alto": pack_id.package_type_id.height/1000 or 1,
                    "largo": pack_id.package_type_id.packaging_length/1000 or 1,
                    "profundidad": pack_id.package_type_id.width/1000 or 1,
                    }
            })
            else:
                for p in items:
                    data.append({
                        "bultos": p.qty_done,
                        "peso": p.product_id.weight or 0,
                        "descripcion": p.move_id.sale_line_id.name or p.product_id.name,
                        "dimensiones": {
                            "alto": 1,
                            "largo": 1,
                            "profundidad": 1
                            }
                    })
        return data

    def get_valor_declarado(self):
        self.ensure_one()
        return sum(self.move_ids_without_package.mapped('sale_line_id.price_subtotal'))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

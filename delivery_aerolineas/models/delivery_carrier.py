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
from .aerolineas import Aerolineas
import json
import base64


class DeliveryCarrier(models.Model):

    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[
        ('aerolineas', "Aerolineas")
    ], ondelete={'aerolineas': lambda recs: recs.write({'delivery_type': 'fixed', 'fixed_price': 0})})
    aerolineas_token = fields.Char("token de Aerolineas", groups="base.group_system")

    shipper_contact = fields.Many2one('res.partner', string="Contacto de entrega", help="Contacto de entrega que se notificara a Aerolineas")

    service_type = fields.Selection(
        selection=[('MID', 'Same Day'), ('DSI', 'Next Day')],
        string="Tipo de contrato")
    
    commodityType = fields.Char("commodityType", groups="base.group_system")
    paymentMode = fields.Char("paymentMode", groups="base.group_system")
    primaryId = fields.Char("primaryId", groups="base.group_system")
    account = fields.Char("account", groups="base.group_system")

    def aerolineas_send_shipping(self, pickings):
        # Me quedo con las transferencias que tengan productos de aerolineas, si no hay ningun producto de aerolinea entonces tiro un error
        pickings = pickings.filtered(lambda l: any(line.product_id.aerolineas_product for line in l.move_line_ids_without_package))
        if not pickings:
            raise ValidationError("No hay ningun producto de aerolineas para enviar.\nPor favor configure los productos o modifique el transportista y vuelva intentar.")

        res = []
        pickings_with_errors = []
        labels_with_errors = []
        aerolineas = Aerolineas(self.aerolineas_token)

        for picking in pickings:
            error = False
            tracking_number = ''
            try:
                aerolineas_data = picking._get_aerolineas_data()
                aerolineas_res = aerolineas.get_book(aerolineas_data)
                bultos = aerolineas_res[0].get('shipments')
                if bultos:
                    tracking_number = bultos[0].get('airWaybill')
                res.append({
                    'exact_price': 0.0,
                    'tracking_number': tracking_number
                })
                log_message = "Envío creado para Aerolineas<br/><b>Número de seguimiento:</b> {}".format(
                    tracking_number
                )
                picking.message_post(body=log_message)
            except Exception as e:
                pickings_with_errors.append('{}: {}'.format(picking.name, e.args[0]))
                picking.message_post(body="Hubo un error al intentar generar el envío en Aerolineas.")
                error = True

            if tracking_number:
                try:
                    label = aerolineas.get_label(tracking_number)
                    attachments = [
                        ('Etiqueta {}.pdf'.format(tracking_number), base64.b64decode((json.loads(label.text).get("base64Content").split(',')[1])))
                     ]
                    picking.message_post(body='Etiqueta generada', attachments=attachments)
                except Exception as e:
                    labels_with_errors.append('{}: {}'.format(picking.name, e.args[0]))
                    picking.message_post(body="Hubo un error al intentar descargar la etiqueta de Aerolineas.")
                    error = True
            if not error:
                picking.env.cr.commit()

        errors = ''
        if pickings_with_errors:
            errors += '{} {}'.format(
                'No se pudieron enviar a Aerolineas los siguientes remitos: ',
                '\n'.join(pickings_with_errors)
            )
        if labels_with_errors:
            errors += '{} {}'.format(
                'No se pudieron enviar generar los etiquetas de los siguientes remitos: ',
                '\n'.join(labels_with_errors)
            )

        if errors:
            raise ValidationError(errors)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

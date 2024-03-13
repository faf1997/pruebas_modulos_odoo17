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
from .andreani import Andreani
from itertools import groupby


class DeliveryCarrier(models.Model):

    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[
        ('andreani', "Andreani")
    ], ondelete={'andreani': lambda recs: recs.write({'delivery_type': 'fixed', 'fixed_price': 0})})
    andreani_contract = fields.Char("Contrato Andreani", groups="base.group_system")
    andreani_user = fields.Char("Usuario Andreani", groups="base.group_system")
    andreani_password = fields.Char("Password Andreani", groups="base.group_system")

    def andreani_rate_shipment(self, order):
        return {'price': 0.0, 'success': True, 'warning_message': False, 'error_message': False}

    def andreani_send_shipping(self, pickings):
        res = []
        pickings_with_errors = []
        labels_with_errors = []
        try:
            andreani = Andreani(self.andreani_user, self.andreani_password, self.andreani_contract)
        except Exception as e:
            raise ValidationError("Error al intentar conectarse a Andreani: </br>{}".format(e.args[0]))

        for picking in pickings:                
            error = False
            tracking_number = ''
            try:
                andreani_res = andreani.get_order(
                    self._get_andreani_order_data(
                        picking.company_id,
                        picking.partner_id,
                        picking.move_line_ids_without_package
                    )
                )
                bultos = andreani_res.get('bultos')
                if bultos:
                    tracking_number = bultos[0].get('numeroDeEnvio')
                res.append({
                    'exact_price': 0.0,
                    'tracking_number': tracking_number
                })
                log_message = "Envío creado para Andreani<br/><b>Número de seguimiento:</b> {}<br/>".format(
                    tracking_number
                )
                picking.message_post(body=log_message)
            except Exception as e:
                pickings_with_errors.append('{}: {}'.format(picking.name, e.args[0]))
                picking.message_post(body="Hubo un error al intentar generar el envío en Andreani.")
                error = True

            if tracking_number:
                try:
                    label = andreani.get_label(tracking_number)
                    attachments = [
                        ('Etiqueta {}.pdf'.format(tracking_number), label.content)
                     ]
                    picking.message_post(body='Etiqueta generada', attachments=attachments)
                except Exception as e:
                    labels_with_errors.append('{}: {}'.format(picking.name, e.args[0]))
                    picking.message_post(body="Hubo un error al intentar descargar la etiqueta de Andreani.")
                    error = True

            if not error:
                picking.env.cr.commit()

        errors = ''
        if pickings_with_errors:
            errors += '{} {}'.format(
                'No se pudieron enviar a andreani los siguientes remitos: ',
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

    def andreani_get_tracking_link(self, picking):
        return f'https://www.andreani.com/#!/informacionEnvio/{picking.carrier_tracking_ref}'

    def _get_andreani_order_data(self, company, partner, lines):
        data = {
            "origen": self._get_andreani_origin(company),
            "destino": self._get_andreani_destination(partner),
            "remitente": self._get_andreani_partner_data(company),
            "destinatario": [self._get_andreani_partner_data(partner)],
            "bultos": []
        }
        # Ordeno las lineas del remito y las agrupo por el paquete de destino
        lines = lines.sorted(lambda l: l.result_package_id.id or 0)
        for group, lin in groupby(lines, key=lambda l: l.result_package_id.id or 0):
            line = list(lin)
            # Si el grupo pertenece a un paquete de destino entonces cargo el peso del paquete y las dimensiones del paquete
            if group != 0:
                package_type_id = line[0].result_package_id.package_type_id
                data["bultos"].append({"kilos": line[0].result_package_id.weight, "volumenCm": package_type_id.packaging_length*package_type_id.width*package_type_id.height/1000})
            else:
                # Si el grupo no pertenece a ningun paquete (se enviaron los productos sueltos), entonces agrego 1
                # bulto por cada producto suelto con el peso y el volumen de cada producto
                for l in line:
                    data["bultos"].append({"kilos": l.product_id.weight, "volumenCm": l.product_id.volume*1000000})
        return data

    def _get_andreani_origin(self, company):
        return {
            "postal": {
                "codigoPostal": company.zip or '',
                "calle": company.street or "",
                "numero": company.street2 or "",
                "localidad": "{} ({})".format(company.city, company.state_id.name) if company.state_id
                             else "{}".format(company.city or ""),
                "region": "",
                "pais": company.country_id.name or "Argentina",
            }
        }

    def _get_andreani_destination(self, partner):
        return {
            "postal": {
                "codigoPostal": partner.zip or "",
                "calle": partner.street or "",
                "numero": partner.street2 or "",
                "localidad": "{} ({})".format(partner.city, partner.state_id.name) if partner.state_id
                             else "{}".format(partner.city or ""),
                "region": "",
                "pais": partner.country_id.name or "Argentina",
            }
        }

    def _get_andreani_partner_data(self, partner):
        return {
            "nombreCompleto": partner.name or "",
            "email": partner.email or "",
            "documentoTipo": "",
            "documentoNumero": partner.vat or "",
            "telefonos": [
                {
                    "tipo": 1,
                    "numero": partner.phone or partner.mobile or ""
                }
            ]
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

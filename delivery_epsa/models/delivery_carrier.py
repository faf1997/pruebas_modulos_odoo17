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
from .epsa import Epsa


class DeliveryCarrier(models.Model):

    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection(selection_add=[
        ('epsa', "EPSA")
    ], ondelete={'epsa': lambda recs: recs.write({'delivery_type': 'fixed', 'fixed_price': 0})})

    epsa_token = fields.Char("token de EPSA", groups="base.group_system")

    epsa_servicio = fields.Char("Servicio de EPSA", groups="base.group_system")

    epsa_sucursal = fields.Char("Codigo de sucursal de EPSA", groups="base.group_system")

    epsa_nombre_etiqueta = fields.Char("Nombre de la etiqueta de EPSA", groups="base.group_system")

    def epsa_send_shipping(self, pickings):
        res = []
        pickings_with_errors = []
        labels_with_errors = []

        try:
            epsa = Epsa(self.epsa_token, self.epsa_servicio, self.epsa_sucursal, self.epsa_nombre_etiqueta)
        except Exception as e:
            raise ValidationError("Error al intentar conectarse a Epsa: </br>{}".format(e.args[0]))
        
        for picking in pickings:
            error = False
            guia = False
            # Intento generar la guia en EPSA
            try:
                epsa_res = epsa.post_guia(picking._get_epsa_data())
                guia = epsa_res.get('guia')
                # La funcion esta tiene que devolver una respuesta en este formato para no romper con el comportamiento base
                res.append({
                    'exact_price': epsa_res.get('importe', 0.0),
                    'tracking_number': guia
                })
                log_message = "Envío creado para EPSA<br/><b>Número de guia:</b> {}<br/>".format(guia)
                picking.message_post(body=log_message)
            except Exception as e:
                pickings_with_errors.append('{}: {}'.format(picking.name, e.args[0]))
                picking.message_post(body="Hubo un error al intentar generar el envío en EPSA.")
                error = True
            # Si pude generar la guia entonces intento obtener las etiquetas
            if guia:
                try:
                    label = epsa.get_etiquetas([guia])
                    # Convierto la etiqueta de html a pdf y lo adjunto al remito
                    attachments = [
                        ('Etiqueta {}.pdf'.format(guia), self.env['ir.actions.report']._run_wkhtmltopdf([label.text.replace('\n','')]))
                     ]
                    picking.message_post(body='Etiqueta generada', attachments=attachments)
                except Exception as e:
                    labels_with_errors.append('{}: {}'.format(picking.name, e.args[0]))
                    picking.message_post(body="Hubo un error al intentar descargar la etiqueta de EPSA.")
                    error = True
            if not error:
                picking.env.cr.commit()

        errors = ''
        if pickings_with_errors:
            errors += '{} {}'.format(
                'No se pudieron enviar a epsa los siguientes remitos: ',
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

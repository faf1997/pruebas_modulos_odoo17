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

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64


class GenerateAutomaticDebitFilesWizard(models.TransientModel):
    _name = 'generate.automatic.debit.files.wizard'
    _description = 'Wizard para Generacion de archivos de debitos automaticos'

    date_from = fields.Date(string='Desde', required=True)
    date_to = fields.Date(string='Hasta', required=True)
    payment_term_id = fields.Many2one(
        'account.payment.term', 
        'Plazo de pago', 
        required=True, 
        domain=[('is_automatic_debit', '=', True)]
    )

    @api.constrains('date_from', 'date_to')
    def check_dates(self):
        if self.date_from > self.date_to:
            raise ValidationError("La fecha desde no puede ser mayor a la fecha hasta.")

    def get_invoices(self):
        """ Este método se utiliza al generar el archivo txt, y busca las facturas 
        abiertas que pertenezcan al rango de fechas y plazo de pago seleccionados.

        Returns:
            [recordset]: Facturas buscadas.
        """
        return self.env['account.move'].search([
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', '=', 'not_paid'),
            ('invoice_payment_term_id', '=', self.payment_term_id.id),
            ('invoice_date', '<=', self.date_to),
            ('invoice_date', '>=', self.date_from)
        ])

    def get_card(self, partner, card_type):
        """ Este método se utiliza al generar el archivo txt, y busca la 
        tarjeta por defecto para el partner del tipo seleccionado.

        Returns:
            [record]: Tarjeta buscada.
        """
        cards = partner.prisma_card_ids.filtered(lambda x: x.card_type == card_type and x.default_card)
        return cards[0] if cards else False

    def generate_header_file(self, create_datetime, company, card_type):
        """ Genero la cabecera del archivo

        Args:
            create_datetime ([datetime]): Fecha de creacion de la presentación.
            company ([record]): Compañia
            card_type ([str]): Codigo de tipo de tarjeta.

        Returns:
            [str]: Línea de cabecera.
        """

        # Este campo siempre es 0, significa que es la cabecera.
        header = '0'
        # Se completa con el codigo según el tipo de tarjeta.
        header += card_type.ljust(8)
        # Se agrega el nro de establecimiento (un dato de la compañia)
        header += company.prisma_mastercard.zfill(10) \
            if card_type == 'DEBLIMC' \
            else company.prisma_visa.zfill(10)
        # Campo fijo "900000    "
        header += '900000'.ljust(10)
        # Dia de la presentación en formato AAAAMMDD
        header += create_datetime.strftime('%Y%m%d')
        # Hora de armado del txt en formato HHMM
        header += create_datetime.strftime('%H%M')
        # Campo Fijo '0  ', más un campo opcional de 55 caracteres que se dejan en blanco.
        header += '0'.ljust(58)
        # Fin de línea.
        header += '*\r\n'
        return header

    def generate_footer_file(self, create_datetime, lines_qty, amount_total, company, card_type):
        """ Genero el cierre del archivo

        Args:
            create_datetime ([datetime]): Fecha de creacion de la presentación.
            lines_qty ([int]): Cantidad de lineas de facturas del archivo.
            amount_total ([float]): Importe total de las líneas.
            company ([record]): Compañia
            card_type ([str]): Codigo de tipo de tarjeta.

        Returns:
            [str]: Línea de cierre de archivo.
        """
        # Este campo siempre es 9, significa que es el cierre.
        footer = '9'
        # Se completa con el codigo según el tipo de tarjeta.
        footer += card_type.ljust(8)
        # Se agrega el nro de establecimiento (un dato de la compañia)
        footer += company.prisma_mastercard.zfill(10) \
            if card_type == 'DEBLIMC' \
            else company.prisma_visa.zfill(10)
        # Campo fijo "900000    "
        footer += '900000'.ljust(10)
        # Dia de la presentación en formato AAAAMMDD
        footer += create_datetime.strftime('%Y%m%d')
        # Hora de armado del txt en formato HHMM
        footer += create_datetime.strftime('%H%M')
        # Cantidad de lineas de facturas del archivo
        footer += str(lines_qty).zfill(7)
        # Importe total de todas las lineas de las facturas con dos decimales y sin punto.
        footer += ('%.2f' % (amount_total)).replace('.','').zfill(15)
        # Campo opcional dejado en blanco, más el fin de línea.
        footer += '*\r\n'.rjust(39)
        return footer

    def generate_body_file(self, card, invoice, create_datetime):
        """ Genero el cuerpo del archivo

        Args:
            card ([record]): Tarjeta usada para el débito.
            invoice ([record]): Factura para generar la línea.
            create_datetime ([datetime]): Fecha de creacion de la presentación.

        Returns:
            [str]: Línea de cuerpo del archivo.
        """
        # Este campo siempre es 1, significa que es una línea del cuerpo del txt.
        body = '1'
        # Nro de tarjeta
        body += card.card_number
        # Campo fijo "   "
        body += ''.ljust(3)
        # Nro de factura
        body += invoice.name_get()[0][1][-8:].zfill(8)
        # Dia de la presentación en formato AAAAMMDD
        body += create_datetime.strftime('%Y%m%d')
        # "0005" Por ser débito.
        body += '5'.zfill(4)
        # Importe de la factura con dos decimales y sin punto.
        body += ('%.2f' % (invoice.amount_residual_signed)).replace('.','').zfill(15)
        # ID asignado a una tarjeta para todas las presentaciones.
        body += invoice.partner_id.id_prisma.zfill(15)
        # 'E' si es débito nuevo, caso contrario un espacio.
        body += 'E'.ljust(29)
        # Fin de línea.
        body += '*\r\n'
        return body

    def generate_files(self):
        """ Método que genera el archivo de débitos automáticos para Prisma y crea su registro correspondiente.
        Para crear este archivo se sigue la documentación adjuntada dentro de este mismo modulo en /docs/.

        Returns:
            [action]: Vista del registro generado.
        """
        company = self.payment_term_id.company_id
        card_type = self.payment_term_id.card_type

        # Traemos las facturas sobre las cuales iteraremos para generar el archivo.
        invoices = self.get_invoices()

        # Validaciones
        if not invoices:
            raise ValidationError('No se encontraron facturas.')

        if not company.prisma_mastercard and card_type == 'DEBLIMC':
            raise ValidationError('No se encontró el número de establecimiento MasterCard en la compañia')
        elif not company.prisma_visa and card_type != 'DEBLIMC':
            raise ValidationError('No se encontró el número de establecimiento VISA en la compañia')

        create_datetime = fields.Datetime.now()
        lines_qty, amount_total = 0, 0

        # Obtenemos la cabecera del archivo
        file_text = self.generate_header_file(create_datetime, company, card_type)

        for invoice in invoices:
            if not invoice.partner_id.id_prisma:
                raise ValidationError('El cliente {} no posee ID prisma.'.format(invoice.partner_id.name))
            
            # Buscamos la tarjeta que necesitamos del partner.
            card = self.get_card(invoice.partner_id, card_type)
            if not card:
                raise ValidationError('No se encontró una tarjeta para débito automático por defecto en el cliente, '
                                      'del tipo configurado en el medio de pago.')
            lines_qty += 1
            amount_total += round(invoice.amount_residual_signed, 2)
            # Agregamos una línea por cada factura.
            file_text += self.generate_body_file(card, invoice, create_datetime)

        # Finalmente se agrega el cierre del archivo con la cantidad de lineas y el monto total.
        file_text += self.generate_footer_file(create_datetime, lines_qty, amount_total, company, card_type)

        # Creamos el registro de débito automático y guardamos el archivo.
        automatic_debit = self.env['automatic.debit.file'].create({
            'date_to': self.date_to,
            'date_from': self.date_from,
            'file': base64.b64encode(file_text.encode()),
            'filename': card_type + '.txt',
            'generation_datetime': create_datetime,
            'payment_term_id': self.payment_term_id.id
        })
        automatic_debit.invoice_ids = [(0, 0, {'invoice_id': invoice.id, 'to_pay': True}) for invoice in invoices]

        # Devolvemos la vista con el debito automatico creado.
        return {
            'type': 'ir.actions.act_window',
            'name': 'Archivo débito automático',
            'view_mode': 'form',
            # 'view_type': 'form',
            'res_model': 'automatic.debit.file',
            'res_id': automatic_debit.id
        }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

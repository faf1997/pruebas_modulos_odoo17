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
from datetime import datetime

from l10n_ar_api.presentations import presentation
from odoo import models, fields
from odoo.exceptions import ValidationError


class PerceptionArba(models.Model):
    _name = 'perception.arba'

    def _get_invoice_currency_rate(self, invoice):
        rate = 1
        currency_lines = invoice.line_ids.filtered(lambda x: x.amount_currency).sorted(
            lambda x: x.product_id, reverse=True
        )  # Las cuentas de ingresos/gastos
        if (invoice.company_id.currency_id != invoice.currency_id) and currency_lines:
            line_currency = currency_lines[0]
            rate = abs((line_currency.credit + line_currency.debit) / line_currency.amount_currency)
        return rate

    def _get_tipo(self, p):
        if p.move_id.move_type == 'out_invoice':
            if p.move_id.voucher_type_id.is_credit_invoice:
                return 'I' if p.move_id.voucher_type_id.is_debit_note else 'E'
            else:
                return 'D' if p.move_id.voucher_type_id.is_debit_note else 'F'
        else:
            return 'H' if p.move_id.voucher_type_id.is_credit_invoice else 'C'

    def _get_sign(self, p):
        return '-' if p.move_id.move_type == 'out_refund' else '0'

    def _get_state_b(self):
        return self.env.ref('base.state_ar_b').id

    def partner_document_type_not_cuit(self, partner):
        return partner.partner_document_type_id != self.env.ref('l10n_ar_afip_tables.partner_document_type_80')

    def create_line(self, presentation_arba, perception):

        line = presentation_arba.create_line()

        vat = perception.move_id.partner_id.vat

        perception_date = perception.move_id.invoice_date.strftime('%d/%m/%Y')

        line.cuit = "{0}-{1}-{2}".format(vat[0:2], vat[2:10], vat[-1:])
        line.fechaPercepcion = perception_date
        line.tipoComprobante = self._get_tipo(perception)
        line.letraComprobante = perception.move_id.voucher_type_id.denomination_id.name
        split_voucher_name = perception.move_id.voucher_name.split('-')
        if split_voucher_name and any(not l.isdigit() for l in split_voucher_name):
            msg = "La factura {} contiene caracteres inválidos (solamente se permiten números y guiones)"
            raise ValidationError(msg.format(perception.move_id.name))
        line.numeroSucursal = split_voucher_name[0][-4:] if len(split_voucher_name) > 1 else '0'.zfill(4)
        line.numeroEmision = split_voucher_name[1][:8] if len(split_voucher_name) > 1 else perception.move_id.voucher_name[-8:]
        line.basePercepcion = '{0:.2f}'.format(
            perception.base * self._get_invoice_currency_rate(perception.move_id)).replace('.', ',')
        line.importePercepcion = '{0:.2f}'.format(
            perception.amount * self._get_invoice_currency_rate(perception.move_id)).replace('.', ',')
        line.tipoOperacion = 'A'
        line.sign = self._get_sign(perception)

    def generate_file(self):
        if self.version == '1.1':
            presentation_arba = presentation.Presentation("arba", "percepciones")
        elif self.version == '1.2':
            presentation_arba = presentation.Presentation("arba", "percepciones2")

        perceptions = self.env['account.invoice.perception'].search([
            ('move_id.voucher_type_id', '!=', False),
            ('move_id.date', '>=', self.date_from),
            ('move_id.date', '<=', self.date_to),
            ('perception_id.type', '=', 'gross_income'),
            ('perception_id.state_id', '=', self._get_state_b()),
            ('move_id.state', '=', 'posted'),
            ('perception_id.type_tax_use', '=', 'sale'),
            ('move_id.company_id', '=', self.company_id.id)
        ]).sorted(key=lambda r: (r.move_id.date, r.id))

        missing_vats = set()
        invalid_doctypes = set()
        invalid_vats = set()

        for p in perceptions:
            vat = p.move_id.partner_id.vat
            if not vat:
                missing_vats.add(p.move_id.name_get()[0][1])
            elif len(vat) < 11:
                invalid_vats.add(p.move_id.name_get()[0][1])
            if self.partner_document_type_not_cuit(p.move_id.partner_id):
                invalid_doctypes.add(p.move_id.name_get()[0][1])

            # si ya encontro algun error, que no siga con el resto del loop porque el archivo no va a salir
            # pero que siga revisando las percepciones por si hay mas errores, para mostrarlos todos juntos
            if missing_vats or invalid_doctypes or invalid_vats:
                continue
            try:
                self.create_line(presentation_arba, p)
            except ValidationError as e:
                raise e
            except Exception as e:
                raise ValidationError(e)

        if missing_vats or invalid_doctypes or invalid_vats:
            errors = []
            if missing_vats:
                errors.append("Los partners de las siguientes facturas no poseen numero de CUIT:")
                errors.extend(missing_vats)
            if invalid_doctypes:
                errors.append("El tipo de documento de los partners de las siguientes facturas no es CUIT:")
                errors.extend(invalid_doctypes)
            if invalid_vats:
                errors.append("Los partners de las siguientes facturas poseen numero de CUIT erroneo:")
                errors.extend(invalid_vats)
            raise ValidationError("\n".join(errors))

        else:
            self.file = presentation_arba.get_encoded_string()
            self.filename = 'AR-{vat}-{month}{period}-{presentation_type}{activity}-LOTE{lot}.TXT'.format(
                vat=self.company_id.vat,
                month=self.date_from.strftime('%Y%m'),
                period=self.period,
                presentation_type=(self.presentation_type == 'received' and 'P' or 'D') if self.presentation_type else '',
                activity=self.activity,
                lot=self.lot,
            )

    name = fields.Char(string='Nombre', required=True)
    date_from = fields.Date(string='Desde', required=True)
    date_to = fields.Date(string='Hasta', required=True)
    activity = fields.Char(string='Actividad', required=True, default='7')
    version = fields.Selection(
        selection=[
            ('1.1', '1.1'),
            ('1.2', '1.2'),
        ],
        string='Versión',
        required=True
    )
    period = fields.Selection(
        [('0', "Mes"), ('1', "Primera quincena"), ('2', "Segunda quincena")],
        string="Período",
        required=True
    )
    presentation_type = fields.Selection(
        string="Tipo",
        selection=[
            ('received', 'Percibido'),
            ('accrued', 'Devengado'),
        ]
    )
    lot = fields.Char(string='Lote', required=True, default='0')
    file = fields.Binary(string='Archivo', filename="filename")
    filename = fields.Char(string='Nombre Archivo')
    company_id = fields.Many2one(
        'res.company',
        string='Empresa',
        required=True,
        readonly=True,
        change_default=True,
        default=lambda self: self.env['res.company']._company_default_get('perception.arba')
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from odoo import models, fields
from odoo.exceptions import ValidationError
from l10n_ar_api.presentations import presentation


class PerceptionTucuman(models.Model):
    _name = 'perception.tucuman'
    _description = 'Percepción Tucumán'

    name = fields.Char('Nombre', required=True)
    date_from = fields.Date('Desde', required=True)
    date_to = fields.Date('Hasta', required=True)
    file = fields.Binary(string='Archivo DATOS.TXT', filename="filename")
    filename = fields.Char(string='Nombre Archivo Datos')
    file_retper = fields.Binary(string='Archivo RETPER.TXT', filename="filename_retper")
    filename_retper = fields.Char(string='Nombre Archivo Retper')
    company_id = fields.Many2one(
        'res.company',
        string='Empresa',
        required=True,
        readonly=True,
        change_default=True,
        default=lambda self: self.env['res.company']._company_default_get('perception.tucuman')
    )

    def _get_invoice_currency_rate(self, invoice):
        rate = 1
        currency_lines = invoice.line_ids.filtered(lambda x: x.amount_currency).sorted(
            lambda x: x.product_id, reverse=True
        )  # Las cuentas de ingresos/gastos
        if (invoice.company_id.currency_id != invoice.currency_id) and currency_lines:
            line_currency = currency_lines[0]
            rate = abs((line_currency.credit + line_currency.debit) / line_currency.amount_currency)
        return rate

    def partner_document_type_not_cuit(self, partner):
        return partner.partner_document_type_id != self.env.ref('l10n_ar_afip_tables.partner_document_type_80')

    def create_line_perception(self, presentation_padron_tucuman, perception):
        line = presentation_padron_tucuman.create_line()

        invoice = perception.move_id

        line.fecha = invoice.invoice_date.strftime('%Y%m%d')
        cuit = self.env['codes.models.relation'].get_code(
                    'partner.document.type',
                    invoice.partner_id.partner_document_type_id.id
                )
        line.tipoDoc = int(cuit) or '99'
        line.documento = invoice.partner_id.vat
        line.tipoComprobante = invoice.voucher_type_id.code
        line.letraComprobante = invoice.voucher_type_id.denomination_id.name

        split_voucher_name = invoice.voucher_name.split('-')
        if split_voucher_name and any(not l.isdigit() for l in split_voucher_name):
            msg = "La factura {} contiene caracteres inválidos (solamente se permiten números y guiones)"
            raise ValidationError(msg.format(invoice.name))

        line.codLugarEmision = split_voucher_name[0][-4:] if len(split_voucher_name) > 1 else '0'.zfill(4)
        line.numero = split_voucher_name[1][:8] if len(split_voucher_name) > 1 else invoice.voucher_name[-8:]
        line.baseCalculo = '{0:.2f}'.format(
             perception.base * self._get_invoice_currency_rate(invoice))
        line.alicuota = '{0:.3f}'.format((perception.amount / perception.base) * 100)
        line.monto = '{0:.2f}'.format(
             perception.amount * self._get_invoice_currency_rate(invoice))

    def create_line_retention(self, presentation_padron_tucuman, retention):

        line = presentation_padron_tucuman.create_line()
        line.fecha = retention.payment_id.payment_date.strftime('%Y%m%d')
        cuit = self.env['codes.models.relation'].get_code(
            'partner.document.type',
            retention.payment_id.partner_id.partner_document_type_id.id
        )
        line.tipoDoc = int(cuit) or '99'
        line.documento = retention.payment_id.partner_id.vat
        line.tipoComprobante = '99'
        line.letraComprobante = 'A'
        try:
            line.codLugarEmision = retention.certificate_no.split('-')[0]
            line.numero = retention.certificate_no.split('-')[1]
        except Exception:
            raise ValidationError("El número de retención del pago {} no contiene el formato XXXX-XXXXXXXX".format(
                retention.payment_id.name
            ))
        line.baseCalculo = '{0:.2f}'.format(retention.base)
        line.alicuota = '{0:.3f}'.format((retention.amount / retention.base) * 100)
        line.monto = '{0:.2f}'.format(retention.amount)

    def get_retentions(self):
        return self.env['account.payment.retention'].search([
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('retention_id.type', '=', 'gross_income'),
            ('retention_id.state_id', '=', self.env.ref('base.state_ar_t').id),
            ('payment_id.state', '=', 'posted'),
            ('retention_id.type_tax_use', '=', 'purchase'),
            ('payment_id.company_id', '=', self.company_id.id)
        ]).sorted(key=lambda r: (r.payment_id.payment_date, r.id))

    def get_perceptions(self):
        return self.env['account.invoice.perception'].search([
            ('move_id.date', '>=', self.date_from),
            ('move_id.date', '<=', self.date_to),
            ('perception_id.type', '=', 'gross_income'),
            ('perception_id.state_id', '=', self.env.ref('base.state_ar_t').id),
            ('move_id.state', '=', 'posted'),
            ('perception_id.type_tax_use', '=', 'sale'),
            ('move_id.company_id', '=', self.company_id.id)
        ]).sorted(key=lambda r: (r.move_id.date, r.id))

    def generate_datos(self, perceptions, retentions):
        presentation_padron_tucuman = presentation.Presentation("padron_tucuman", "datos")

        missing_vats = set()
        invalid_doctypes = set()
        invalid_vats = set()
        missing_pos_ar = set()

        for p in perceptions:
            vat = p.move_id.partner_id.vat
            if not vat:
                missing_vats.add(p.move_id.name_get()[0][1])
            elif len(vat) < 11:
                invalid_vats.add(p.move_id.name_get()[0][1])
            if self.partner_document_type_not_cuit(p.move_id.partner_id):
                invalid_doctypes.add(p.move_id.name_get()[0][1])

            # Si ya encontró algún error, que no siga con el resto del loop porque el archivo no va a salir,
            # pero que siga revisando las percepciones por si hay más errores, para mostrarlos todos juntos
            if missing_vats or invalid_doctypes or invalid_vats:
                continue
            try:
                self.create_line_perception(presentation_padron_tucuman, p)
            except ValidationError as e:
                raise e
            except Exception as e:
                raise ValidationError(e)

        for r in retentions:
            vat = r.payment_id.partner_id.vat
            if not vat:
                missing_vats.add(r.payment_id.name_get()[0][1])
            elif len(vat) < 11:
                invalid_vats.add(r.payment_id.name_get()[0][1])
            if self.partner_document_type_not_cuit(r.payment_id.partner_id):
                invalid_doctypes.add(r.payment_id.name_get()[0][1])
            if not r.payment_id.journal_id.pos_ar_id:
                missing_pos_ar.add(r.payment_id.journal_id.name)

            # Si ya encontró algún error, que no siga con el resto del loop porque el archivo no va a salir,
            # pero que siga revisando las retenciones por si hay más errores, para mostrarlos todos juntos
            if missing_vats or invalid_doctypes or invalid_vats or missing_pos_ar:
                continue
            try:
                self.create_line_retention(presentation_padron_tucuman, r)
            except ValidationError as e:
                raise e
            except Exception as e:
                raise ValidationError(e)

        if missing_vats or invalid_doctypes or invalid_vats or missing_pos_ar:
            errors = []
            if missing_vats:
                errors.append("Los partners de las siguientes facturas no poseen número de CUIT:")
                errors.extend(missing_vats)
            if invalid_doctypes:
                errors.append("El tipo de documento de los partners de las siguientes facturas no es CUIT:")
                errors.extend(invalid_doctypes)
            if invalid_vats:
                errors.append("Los partners de las siguientes facturas poseen número de CUIT erroneo:")
                errors.extend(invalid_vats)
            if missing_pos_ar:
                errors.append("Los siguientes diarios no poseen punto de venta:")
                errors.extend(missing_pos_ar)
            raise ValidationError("\n".join(errors))

        else:
            self.file = presentation_padron_tucuman.get_encoded_string()
            self.filename = 'DATOS.TXT'

    def generate_files(self):
        if not self.company_id.vat:
            raise Warning('Falta configuración de CUIT en la empresa')
        perceptions = self.get_perceptions()
        retentions = self.get_retentions()

        self.generate_datos(perceptions, retentions)
        self.generate_retper(perceptions, retentions)

    def generate_retper(self, perceptions, retentions):
        presentation_padron_tucuman_retper = presentation.Presentation("padron_tucuman", "retper")
        
        partners = retentions.mapped('partner_id') | perceptions.mapped('partner_id')
        for partner in partners:
            line = presentation_padron_tucuman_retper.create_line()
            street = '{} {}'.format(partner.street or '', partner.street2 or '')
            line.tipoDoc = 80  # Esta limitado que solo sea con cuits en la obtención de ret y perc,
            line.documento = int(partner.vat)
            line.nombre = '{0:->40s}'.format(partner.name)
            line.domicilio = '{0:->40s}'.format(street or '')
            line.numero = 0
            line.localidad = '{0:->15s}'.format(partner.city or '')
            line.provincia = '{0:->15s}'.format(partner.state_id.name or '')
            line.noUsado = 0  # Llenado con ceros en la API.
            line.codPostal = '{0:->8s}'.format(partner.zip or '')

        self.file_retper = presentation_padron_tucuman_retper.get_encoded_string()
        self.filename_retper = 'RETPER.TXT'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

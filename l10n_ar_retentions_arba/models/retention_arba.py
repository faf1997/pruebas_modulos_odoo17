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

from l10n_ar_api.presentations import presentation
from odoo import models, fields
from odoo.exceptions import ValidationError


class RetentionArba(models.Model):
    _name = 'retention.arba'

    def _get_state_b(self):
        return self.env.ref('base.state_ar_b').id

    def partner_document_type_not_cuit(self, partner):
        return partner.partner_document_type_id != self.env.ref('l10n_ar_afip_tables.partner_document_type_80')

    def create_line(self, presentation_arba, retention):

        line = presentation_arba.create_line()

        vat = retention.payment_id.partner_id.vat

        retention_date = retention.payment_id.date.strftime('%d/%m/%Y')
        line.cuit = "{0}-{1}-{2}".format(vat[0:2], vat[2:10], vat[-1:])
        line.fechaRetencion = retention_date
        try:
            line.numeroSucursal = retention.certificate_no.split('-')[0]
            line.numeroEmision = retention.certificate_no.split('-')[1]
        except Exception:
            raise ValidationError("El número retención del pago {} no contiene el formato XXXX-XXXXXXXX".format(
                retention.payment_id.name
            ))
        line.importeRetencion = '{0:.2f}'.format(retention.amount).replace('.', ',')
        line.tipoOperacion = 'A'

    def generate_file(self):
        presentation_arba = presentation.Presentation("arba", "retenciones")
        retentions = self.env['account.payment.retention'].search([
            ('payment_id.voucher_type_id', '!=', False),
            ('payment_id.journal_id.payment_usage', '=', 'document_book'),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
            ('retention_id.type', '=', 'gross_income'),
            ('retention_id.state_id', '=', self._get_state_b()),
            ('payment_id.state', '=', 'posted'),
            ('retention_id.type_tax_use', '=', 'purchase')
        ]).sorted(key=lambda r: (r.payment_id.date, r.id))

        missing_vats = set()
        invalid_doctypes = set()
        invalid_vats = set()

        for r in retentions:

            vat = r.payment_id.partner_id.vat
            if not vat:
                missing_vats.add(r.payment_id.name_get()[0][1])
            elif len(vat) < 11:
                invalid_vats.add(r.payment_id.name_get()[0][1])
            if self.partner_document_type_not_cuit(r.payment_id.partner_id):
                invalid_doctypes.add(r.payment_id.name_get()[0][1])

            # si ya encontro algun error, que no siga con el resto del loop porque el archivo no va a salir
            # pero que siga revisando las retenciones por si hay mas errores, para mostrarlos todos juntos
            if missing_vats or invalid_doctypes or invalid_vats:
                continue
            try:
                self.create_line(presentation_arba, r)
            except ValidationError as e:
                raise e
            except Exception as e:
                raise ValidationError(e)

        if missing_vats or invalid_doctypes or invalid_vats:
            errors = []
            if missing_vats:
                errors.append("Los partners de los siguientes pagos no poseen numero de CUIT:")
                errors.extend(missing_vats)
            if invalid_doctypes:
                errors.append("El tipo de documento de los partners de los siguientes pagos no es CUIT:")
                errors.extend(invalid_doctypes)
            if invalid_vats:
                errors.append("Los partners de los siguientes pagos poseen numero de CUIT erroneo:")
                errors.extend(invalid_vats)
            raise ValidationError("\n".join(errors))

        else:
            self.file = presentation_arba.get_encoded_string()
            self.filename = 'AR-{vat}-{period}{fortnight}-{activity}-LOTE{lot}.TXT'.format(
                vat=self.company_id.vat,
                period=self.date_from.strftime('%Y%m'),
                fortnight=self.fortnight,
                activity=self.activity,
                lot=self.lot,
            )

    name = fields.Char(string='Nombre', required=True)
    date_from = fields.Date(string='Desde', required=True)
    date_to = fields.Date(string='Hasta', required=True)
    activity = fields.Char(string='Actividad', required=True, default='6')
    fortnight = fields.Char(string='Quincena', required=True, default='0')
    lot = fields.Char(string='Lote', required=True, default='0')
    file = fields.Binary(string='Archivo', filename="filename")
    filename = fields.Char(string='Nombre Archivo')
    company_id = fields.Many2one(
        'res.company',
        string='Empresa',
        required=True,
        readonly=True,
        change_default=True,
        default=lambda self: self.env['res.company']._company_default_get('retention.arba')
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

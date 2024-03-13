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

from l10n_ar_api.presentations import presentation
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime
import base64


class PerceptionAgip(models.Model):
    _name = 'perception.agip'
    _description = 'Perception/retention Agip'

    def get_presentation_type(self):
        return 'percepciones_v3' if self.version == 'v3' else 'percepciones'

    def _get_invoice_currency_rate(self, invoice):
        rate = 1
        if invoice.move_id.line_ids:
            move = invoice.move_id.line_ids[0]
            if move.amount_currency != 0:
                rate = abs((move.credit + move.debit) / move.amount_currency)
        return rate

    def validate_origins(self, perceptions):
        errors = []
        if any(not (p.move_id.reversed_entry_id or p.move_id.fce_associated_document_ids.associated_invoice_id) for p in perceptions):
            errors.append("Error! Las siguientes notas de credito no poseen origen:")
            errors.extend(perceptions.filtered(lambda l: not (l.move_id.reversed_entry_id or l.move_id.fce_associated_document_ids.associated_invoice_id)).mapped(
                lambda r: r.move_id.name))
            raise ValidationError("\n".join(errors))

    def create_perception_line(self, presentation_agip, perception):

        line = presentation_agip.create_line()

        invoice = perception.move_id
        origin_invoice = invoice.reversed_entry_id or (
            invoice.fce_associated_document_ids[0].associated_invoice_id if invoice.fce_associated_document_ids else False
        ) if invoice.move_type == 'out_refund' else False
        line.tipoOperacion = 2
        line.numeroCertificado = ''
        line.codigoDeNorma = self.regime_code

        # Monto sujeto a percepcion
        base_amount = perception.base
        perception_amount = perception.amount
        aliquot = 100 * perception_amount / base_amount if base_amount != 0 else 0
        line.alicuota = "{0:.2f}".format(aliquot).replace('.', ',')
        document_types = {
            'CDI': '1',
            'CUIL': '2',
            'CUIT': '3'
        }
        iva_situations = {
            self.env.ref('l10n_ar.ar_fiscal_position_ivari'): '1',
            self.env.ref('l10n_ar.ar_fiscal_position_ex'): '3',
            self.env.ref('l10n_ar.ar_fiscal_position_mon'): '4'
        }
        if origin_invoice:
            invoice_number = invoice.voucher_name.replace("-", "")
            line.numeroNC = invoice_number[-12:] if len(invoice_number) > 12 else invoice_number
            line.fechaNC = invoice.invoice_date.strftime('%d/%m/%Y')
            line.montoNC = '{0:.2f}'.format(invoice.amount_untaxed).replace('.', ',')
            
            if origin_invoice.is_credit_invoice:
                origin_type = "10" if not origin_invoice.is_debit_note and origin_invoice.move_type == 'out_invoice' else "13"
            else:
                origin_type = "01" if not origin_invoice.is_debit_note and origin_invoice.move_type == 'out_invoice' else "09"

            line.tipoComprobante = origin_type
            line.letraComprobante = origin_invoice.voucher_type_id.denomination_id.name if origin_type in ('01', '10') else ''
            line.numeroComprobante = origin_invoice.voucher_name.replace("-", "")
            line.numeroDocRetenido = invoice.partner_id.vat
            
            p = self.env['account.invoice.perception'].search([
                ('perception_id.type', '=', 'gross_income'),
                ('perception_id.state_id', '=', self.env.ref('base.state_ar_c').id),
                ('move_id', '=', origin_invoice.id),
                ('perception_id.type_tax_use', '=', 'sale'),
            ], limit=1)

            #Fecha percepcion original
            line.fecha = p.date_invoice.strftime('%d/%m/%Y') if p else origin_invoice.invoice_date.strftime('%d/%m/%Y') 
            line.percepcionADeducir = '{0:.2f}'.format(perception_amount).replace('.', ',')
        else:
            line.fecha = invoice.invoice_date.strftime('%d/%m/%Y')
            
            if invoice.is_credit_invoice:
                origin_type = "10" if not invoice.is_debit_note and invoice.move_type == 'out_invoice' else "13"
            else:
                origin_type = "01" if not invoice.is_debit_note and invoice.move_type == 'out_invoice' else "09"

            line.tipoComprobante = origin_type
            origin_letter = " " if origin_type not in ['01', '06', '07', '10'] else invoice.voucher_type_id.denomination_id.name
            line.letraComprobante = origin_letter
            line.numeroComprobante = invoice.voucher_name.replace('-', '')
            line.fechaComprobante = invoice.invoice_date.strftime('%d/%m/%Y')
            invoice_amount = invoice.amount_total
            line.montoComprobante = "{0:.2f}".format(invoice_amount).replace('.', ',')
            line.numeroCertificado = ''  # Para percepciones siempre es vacio
            document_type = document_types.get(invoice.partner_id.partner_document_type_id.name, "0")
            line.tipoDocRetenido = document_type
            line.numeroDocRetenido = invoice.partner_id.vat
            situation_ib = "4" if document_type != "3" else invoice.partner_id.iibb_situation
            line.situacionIBRetenido = situation_ib
            line.numeroInscripcionIBRetenido = invoice.partner_id.iibb_number if invoice.partner_id.iibb_number else 0
            line.situacionIVARetenido = iva_situations.get(invoice.partner_id.property_account_position_id.ar_fiscal_position_id, "0")
            line.razonSocialRetenido = invoice.partner_id.name[:30]

            # Importe IVA
            tax_amount = 0.0
            if origin_letter in ["A", "M"]:
                for l in invoice.line_ids.filtered(lambda t: t.tax_line_id.is_vat):
                    tax_amount += abs(l.balance)

            other = invoice_amount - tax_amount - base_amount
            line.importeOtrosConceptos = "{0:.2f}".format(other).replace('.', ',')
            line.importeIVA = "{0:.2f}".format(tax_amount).replace('.', ',')
            line.montoSujetoRetencion = "{0:.2f}".format(base_amount).replace('.', ',')
           
            line.retencionPracticada = "{0:.2f}".format(perception_amount).replace('.', ',')
            line.montoTotalRetenido = "{0:.2f}".format(perception_amount).replace('.', ',')

            if self.version == 'v3':
                line.aceptacion = ' '
                line.fechaAceptacionExpresa = ' '
    
    def create_retention_line(self, presentation_agip, retention):

        line = presentation_agip.create_line()
        
        document_types = {
            'CDI': '1',
            'CUIL': '2',
            'CUIT': '3'
        }

        iva_situations = {
            self.env.ref('l10n_ar.ar_fiscal_position_ivari'): '1',
            self.env.ref('l10n_ar.ar_fiscal_position_ex'): '3',
            self.env.ref('l10n_ar.ar_fiscal_position_mon'): '4'
        }

        line.tipoOperacion = 1
        
        line.codigoDeNorma = self.regime_code
        
        line.fecha = retention.payment_id.date.strftime('%d/%m/%Y')
        
        line.tipoComprobante = "03"  # Siempre es orden de pago
        
        line.letraComprobante = " "

        line.numeroComprobante = retention.payment_id.name.split()[1]
        
        line.fechaComprobante = retention.payment_id.date.strftime('%d/%m/%Y')
        
        base_amount = retention.base
        line.montoComprobante = '{0:.2f}'.format(base_amount).replace('.', ',')
        
        # Si es 00 se hace vacio
        line.numeroCertificado = retention.certificate_no if retention.certificate_no != "00" else ''
        
        document_type = document_types.get(retention.payment_id.partner_id.partner_document_type_id.name, "0")
        line.tipoDocRetenido = document_type
        
        line.numeroDocRetenido = retention.payment_id.partner_id.vat
        
        situation_ib = "4" if document_type != "3" else retention.payment_id.partner_id.iibb_situation
        line.situacionIBRetenido = situation_ib
        
        line.numeroInscripcionIBRetenido = retention.payment_id.partner_id.iibb_number if retention.payment_id.partner_id.iibb_number else 0
        
        line.situacionIVARetenido = iva_situations.get(retention.payment_id.partner_id.property_account_position_id.ar_fiscal_position_id, "0")

        line.razonSocialRetenido = retention.payment_id.partner_id.name[:30]

        line.importeOtrosConceptos = "{0:.2f}".format(0.0).replace('.', ',')
        line.importeIVA = "{0:.2f}".format(0.0).replace('.', ',')
        line.montoSujetoRetencion = "{0:.2f}".format(base_amount).replace('.', ',')
        
        retention_amount = retention.amount
        aliquot = 100 * retention_amount / base_amount if base_amount != 0 else 0
        line.alicuota = "{0:.2f}".format(aliquot).replace('.', ',')

        line.retencionPracticada = "{0:.2f}".format(retention_amount).replace('.', ',')
        line.montoTotalRetenido = "{0:.2f}".format(retention_amount).replace('.', ',')

        if self.version == 'v3':
            line.aceptacion = ' '
            line.fechaAceptacionExpresa = ' '
    
    def get_sorted_perc_and_ret_data(self, presentation):
        lines = presentation.lines
        lines.sort(key=lambda l: (datetime.strptime(l.fecha, "%d/%m/%Y"), -int(l.tipoOperacion)))
        eol = '\r\n'
        presentation_string = eol.join(line.get_line_string() for line in lines) + eol
        return base64.b64encode(presentation_string.encode())

    def generate_file(self):
        # Voy a usar este objeto para las líneas de percepciones y retenciones, al fin y al cabo las líneas en sí son
        # las mismas
        presentation_agip = presentation.Presentation("agip", self.get_presentation_type())
        presentation_agip_refund = presentation.Presentation("agip", "percepciones_NC")

        perceptions = self.env['account.invoice.perception'].search([
            ('move_id.voucher_type_id', '!=', False),
            ('move_id.date', '>=', self.date_from),
            ('move_id.date', '<=', self.date_to),
            ('perception_id.type', '=', 'gross_income'),
            ('perception_id.state_id', '=', self.env.ref('base.state_ar_c').id),
            ('move_id.state', '=', 'posted'),
            ('move_id.move_type', '=', 'out_invoice'),
            ('move_id.state', '=', 'posted'),
            ('perception_id.type_tax_use', '=', 'sale'),
            ('move_id.company_id', '=', self.company_id.id)
        ]).sorted(key=lambda r: (r.move_id.date, r.id))

        refund_perceptions = self.env['account.invoice.perception'].search([
            ('move_id.voucher_type_id', '!=', False),
            ('move_id.date', '>=', self.date_from),
            ('move_id.date', '<=', self.date_to),
            ('perception_id.type', '=', 'gross_income'),
            ('perception_id.state_id', '=', self.env.ref('base.state_ar_c').id),
            ('move_id.move_type', '=', 'out_refund'),
            ('move_id.state', '=', 'posted'),
            ('perception_id.type_tax_use', '=', 'sale'),
            ('move_id.company_id', '=', self.company_id.id)
        ]).sorted(key=lambda r: (r.move_id.date, r.id))

        retentions = self.env['account.payment.retention'].search([
            ('payment_id.voucher_type_id', '!=', False),
            ('payment_id.journal_id.payment_usage', '=', 'document_book'),
            ('payment_id.date', '>=', self.date_from),
            ('payment_id.date', '<=', self.date_to),
            ('retention_id.type', '=', 'gross_income'),
            ('retention_id.state_id', '=', self.env.ref('base.state_ar_c').id),
            ('payment_id.state', '=', 'posted'),
            ('retention_id.type_tax_use', '=', 'purchase'),
            ('company_id', '=', self.company_id.id),
        ]).sorted(key=lambda r: (r.payment_id.date, r.id))

        missing_vats = set()
        invalid_vats = set()
        missing_iibb_situation = set()

        if refund_perceptions:
            self.validate_origins(refund_perceptions)
            for p in refund_perceptions:
                vat = p.move_id.partner_id.vat
                if not vat:
                    missing_vats.add(p.move_id.name_get()[0][1])
                elif len(vat) < 11:
                    invalid_vats.add(p.move_id.name_get()[0][1])

                # si ya encontro algun error, que no siga con el resto del loop porque el archivo no va a salir
                # pero que siga revisando las percepciones por si hay mas errores, para mostrarlos todos juntos
                if missing_vats or invalid_vats:
                    continue
                try:
                    self.create_perception_line(presentation_agip_refund, p)
                except ValidationError as e:
                    raise e
                except Exception as e:
                    raise ValidationError(e)

        errors = []
        for p in perceptions:
            vat = p.move_id.partner_id.vat
            if not vat:
                missing_vats.add(p.move_id.display_name)
            elif len(vat) < 11:
                invalid_vats.add(p.move_id.display_name)
            if not p.move_id.partner_id.iibb_situation:
                missing_iibb_situation.add(p.move_id.display_name)

            # si ya encontro algun error, que no siga con el resto del loop porque el archivo no va a salir
            # pero que siga revisando las percepciones por si hay mas errores, para mostrarlos todos juntos
            if missing_vats or invalid_vats or missing_iibb_situation:
                continue
            try:
                self.create_perception_line(presentation_agip, p)
            except ValidationError as e:
                raise e
            except Exception as e:
                errors.append('{}, Para el documento: {}'.format(e, p.move_id.name))

        if errors:
            raise ValidationError("\n".join(errors))

        errors = []
        for r in retentions:
            vat = r.payment_id.partner_id.vat
            if not vat:
                missing_vats.add(r.payment_id.display_name)
            elif len(vat) < 11:
                invalid_vats.add(r.payment_id.display_name)
            if not r.payment_id.partner_id.iibb_situation:
                missing_iibb_situation.add(r.payment_id.display_name)

            # si ya encontro algun error, que no siga con el resto del loop porque el archivo no va a salir
            # pero que siga revisando las percepciones por si hay mas errores, para mostrarlos todos juntos
            if missing_vats or invalid_vats or missing_iibb_situation:
                continue
            try:
                self.create_retention_line(presentation_agip, r)
            except ValidationError as e:
                raise e
            except Exception as e:
                errors.append('{}, Para el documento: {}'.format(e, r.payment_id.name))

        if errors:
            raise ValidationError("\n".join(errors))
        
        if missing_vats or invalid_vats or missing_iibb_situation:
            errors = []
            if missing_vats:
                errors.append("Los partners de las siguientes facturas no poseen número de CUIT:")
                errors.extend(missing_vats)
            if invalid_vats:
                errors.append("Los partners de las siguientes facturas poseen numero de CUIT erróneo:")
                errors.extend(invalid_vats)
            if missing_iibb_situation:
                errors.append("Los partners de los siguientes pagos no poseen situación de IIBB:")
                errors.extend(missing_iibb_situation)
            raise ValidationError("\n".join(errors))

        else:
            self.file = self.get_sorted_perc_and_ret_data(presentation_agip)
            self.file_refunds = presentation_agip_refund.get_encoded_string()
            self.filename = 'per_ret_agip_' + self.version + '_' + self.date_from.strftime('%Y%m%d') + '_' + self.date_to.strftime('%Y%m%d') + '.txt'
            self.filename_refunds = 'per_agip_nc_' + self.date_from.strftime('%Y%m%d') + '_' + self.date_to.strftime('%Y%m%d') + '.txt'
    
    @api.constrains('regime_code')
    def _check_regime(self):
        if self.regime_code < 0 or self.regime_code > 999:
            raise ValidationError('El código de norma debe ser un valor entre 0 y 999')

    name = fields.Char(string='Nombre', required=True)
    regime_code = fields.Integer(string="Código de norma", required=True, default=29)
    date_from = fields.Date(string='Desde', required=True)
    date_to = fields.Date(string='Hasta', required=True)
    file = fields.Binary(string='Archivo perc. y ret.')
    file_refunds = fields.Binary(string='Archivo perc. NC')
    filename = fields.Char(string='Nombre archivo perc. y ret.')
    filename_refunds = fields.Char(string='Nombre archivo perc. NC')
    company_id = fields.Many2one(
        'res.company',
        'Empresa',
        required=True,
        readonly=True,
        change_default=True,
        default=lambda self: self.env.company
    )
    version = fields.Selection([
        ("v3", "3.0"),
        ("v2", "2.0")],
        string="Versión",
        default='v3', required=True,
        help='Versión de AGIP a usar para generar el archivo')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

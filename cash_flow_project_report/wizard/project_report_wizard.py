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

from itertools import groupby
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import base64
from odoo import http
from odoo.http import request
from odoo.addons.web.controllers.main import serialize_exception, content_disposition
from . import future_invoice_report

RECURRING_TYPE = {
    'daily': 'days',
    'weekly': 'weeks',
    'monthly': 'months',
    'yearly': 'years',
}


class ProjectReportWizard(models.TransientModel):
    _name = 'project.report.wizard'

    date_from = fields.Date(
        string='Desde',
        required=True,
    )
    date_to = fields.Date(
        string='Hasta',
        required=True,
    )
    report = fields.Binary(
        string='Reporte'
    )

    @api.constrains('date_from', 'date_to')
    def check_date(self):
        if self.date_from > self.date_to:
            raise ValidationError("La fecha de inicio no puede ser mayor a la fecha fin.")

    @api.model
    def search_periods(self):
        """Busco los periodos para el rango de fechas seteado
        :return: Lista de tuplas con fecha de inicio y fin de cada mes
        """
        # Busco la cantidad de meses entre esas dos fechas
        period_qty = relativedelta(self.date_to, self.date_from)
        # Primer dia del primer mes es el seteado
        first_day = self.date_from
        # Busco el ultimo dia del primer mes
        last_day = self.date_from + relativedelta(day=1) + relativedelta(
            months=1) - relativedelta(days=1)
        months = period_qty.months + period_qty.years * 12
        # Chequeo si el rango seteado es del mismo mes
        if self.date_to.strftime('%m/%Y') == self.date_from.strftime('%m/%Y'):
            periods = [(self.date_to + relativedelta(day=1), self.date_to)]
        else:
            # Agrego las dos fechas para luego comparar
            periods = [(first_day, last_day)]
            # Itero por la cantidad de meses que hay entre fechas
            new_first_day = self.date_from
            for p in range(months - 1):
                new_first_day += relativedelta(day=1) + relativedelta(months=1)
                new_last_day = new_first_day + relativedelta(months=1) - relativedelta(days=1)
                periods.append((new_first_day, new_last_day))
            # Agrego el ultimo mes
            periods.append((self.date_to + relativedelta(day=1), self.date_to))
        return periods

    @api.model
    def search_sale_lines(self, period):
        """Busco las lineas sin facturarorder de las OV"""
        sale_lines = self.env['sale.order.line'].search([
            ('invoice_status', '=', 'to invoice'),
            '|',
            ('order_id.cash_flow_date', '>=', period[0]),
            ('admission_date', '>=', period[0]),
            '|',
            ('order_id.cash_flow_date', '<=', period[1]),
            ('admission_date', '<=', period[1])
        ])
        return sale_lines

    @api.model
    def search_contracts(self, period):
        """Busco los contratos activos para facturar"""
        contracts = self.env['sale.subscription'].search([
            ('stage_id', '=', self.env.ref('sale_subscription.sale_subscription_stage_in_progress').id),
            '|',
            ('date', '=', False),
            ('date', '>=', period[0]),
            '|',
            ('date_start', '=', False),
            ('date_start', '<=', period[1]),
        ])
        return contracts

    def generate_report_xls(self):
        filename = 'Cash-flow-ventas'
        periods = self.search_periods()

        import io
        try:
            import xlwt
        except:
            raise ValidationError('Por favor descargue el modulo xlwt de python '
                                  'desde\nhttp://pypi.python.org/packages/source/x/xlwt/xlwt-0.7.2.tar.gz\ne '
                                  'instalelo.')

        book = xlwt.Workbook()
        style = xlwt.easyxf(
            'font: bold on,height 240,color_index 0X36;'
            'align: horiz left;'
            'borders: left_color 0X36, right_color 0X36, top_color 0X36,'
            ' bottom_color 0X36, left thin, right thin, top thin, bottom thin;'
        )
        style_details = xlwt.easyxf(
            'align: horiz left;'
        )

        stype_details_amount = xlwt.easyxf(
            'align: horiz right;'
        )

        style_subtotal = xlwt.easyxf(
            'font: bold on, height 200, color_index 0X36;'
            'align: horiz left;'
        )
        style_total_amount = xlwt.easyxf(
            'font: bold on, height 200, color_index 0X36;'
            'align: horiz right;'
            'pattern: pattern solid, fore_colour 0x16;'
        )

        row = 0
        sheet = book.add_sheet('Cash flow de venta')

        sheet.col(0).width = 7000
        sheet.col(1).width = 3000
        sheet.col(2).width = 7000

        sheet.write(row, 0, "Cliente", style)
        sheet.write(row, 1, "Tipo", style)
        sheet.write(row, 2, "Referencia", style)
        sheet.write(row, 3, "Moneda", style)

        report_items = []

        col = 4
        sheet.write(row + 1, col - 1, 'USD', style)
        sheet.write(row + 2, col - 1, 'EUR', style)
        for period in periods:

            report_items_of_period = self._get_report_items(period, col)
            if report_items_of_period:
                report_items += report_items_of_period
                rate_usd = self.calculate_period_rate(self.env.ref('base.USD').id, period)
                rate_eur = self.calculate_period_rate(self.env.ref('base.EUR').id, period)
                sheet.write(row, col, period[0].strftime('%m/%Y'), style)
                sheet.write(row + 1, col, str(rate_usd), style)
                sheet.write(row + 2, col, str(rate_eur), style)
                col += 1
        row += 2
        row_sum = row + 1

        report_items.sort(key=lambda x: (x.partner.id, x.report_type.id))
        for key, grouped_by_partner in groupby(report_items, key=lambda x: x.partner.id):

            grouped_by_partner = list(grouped_by_partner)
            sheet.write(row + 1, 0, grouped_by_partner[0].partner.name, style_subtotal)

            for keym, items in groupby(grouped_by_partner, key=lambda x: (x.report_type._name, x.report_type.id)):
                row += 1
                items = list(items)
                if items[0].report_type._name == 'sale.order.line':
                    report_type = 'Venta'
                    amount = items[0].report_type.price_subtotal
                else:
                    report_type = 'Contrato'
                    amount = sum(l.price_subtotal for l in items[0].report_type.recurring_invoice_line_ids)
                sheet.write(row, 1, report_type, style_details)
                sheet.write(row, 2,
                            items[0].report_type.order_id.name + ' - ' + items[0].report_type.product_id.name_get()[
                                0][1] + ' ({})'.format(items[0].report_type.currency_id.name) if items[0].report_type._name == 'sale.order.line' else items[
                                0].report_type.name, style_details)
                sheet.write(row, 3, items[0].report_type.currency_id.name, style_details)
                for item in items:
                    sheet.write(row, item.column, (amount * item.qty) * item.rate, stype_details_amount)

        for x in range(4, col):
            column_start = xlwt.Utils.rowcol_to_cell(row_sum, x)
            column_end = xlwt.Utils.rowcol_to_cell(row, x)
            sheet.write(row + 1, x, xlwt.Formula('SUM(' + column_start + ':' + column_end + ')'), style_total_amount)

        """PARSING DATA AS STRING """
        file_data = io.BytesIO()
        book.save(file_data)
        """STRING ENCODE OF DATA IN SHEET"""
        out = base64.b64encode(file_data.getvalue())
        filename = filename + '.xls'
        self.write({'report': out})

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/binary/download_project?wizard_id=%s&filename=%s' % (self.id, filename + '.xls'),
            'target': 'new',
        }

    def _get_report_items(self, period, col):
        """
        Obtiene los items del reporte segun las oportunidades y los contratos
        :param period: Periodo del cual se buscaran las oportunidades y contratos
        :param col: Numero de columna donde ira el valor
        :return: Lista de FutureInvoiceReport()
        """
        res = []

        sale_lines = self.search_sale_lines(period)
        contracts = self.search_contracts(period)

        for line in sale_lines:
            rate = self.calculate_amount(line, period)
            if line.admission_date \
                    and period[1] >= line.admission_date >= period[0] \
                    or not line.admission_date:
                res.append(
                    future_invoice_report.FutureInvoiceReport(
                        line.order_id.partner_id,
                        col,
                        period,
                        line,
                        1,
                        rate
                    ),
                )

        for contract in contracts:
            qty = self.get_qty_by_month(contract, period)
            rate = self.calculate_amount(contract, period)
            if qty:
                res.append(
                    future_invoice_report.FutureInvoiceReport(
                        contract.partner_id,
                        col,
                        period,
                        contract,
                        qty,
                        rate
                    ),
            )
        return res

    def calculate_amount(self, document, period):
        """ Busco la cotizacion del documento en el periodo dado"""
        rate = 1
        document_currency = document.currency_id
        if document_currency != document.company_id.currency_id:
            rate_period = self.env['res.currency.rate.cash.flow'].search([
                ('name', '<=', period[1]),
                ('name', '>=', period[0]),
                ('currency_id', '=', document.currency_id.id)
            ], order='name desc', limit=1)
            if rate_period:
                rate = rate_period.rate
        return rate

    def calculate_period_rate(self, currency_id, period):
        rate = 1
        rate_period = self.env['res.currency.rate.cash.flow'].search([
            ('name', '<=', period[1]),
            ('name', '>=', period[0]),
            ('currency_id', '=', currency_id)
        ], order='name desc', limit=1)
        if rate_period:
            rate = rate_period.rate
        return rate

    def get_qty_by_month(self, document, period):
        """ Busco la cantidad de veces que aparece un contrato en un periodo dado"""
        recurring_invoices = []
        recurring = document.template_id.recurring_interval
        next_invoice = document.date_start
        while next_invoice <= period[1]:
            recurring_invoices.append(next_invoice.strftime('%m/%Y'))
            new_dict = {RECURRING_TYPE.get(document.template_id.recurring_rule_type): recurring}
            next_invoice += relativedelta(**new_dict)
        qty = recurring_invoices.count(period[0].strftime('%m/%Y'))
        return qty


class ProjectReportReport(http.Controller):
    @http.route('/web/binary/download_project', type='http', auth="public")
    @serialize_exception
    def download_project(self, debug=1, wizard_id=0, filename=''):
        """ Descarga un documento cuando se accede a la url especificada en http route.
        :param debug: Si esta o no en modo debug.
        :param int wizard_id: Id del modelo que contiene el documento.
        :param filename: Nombre del archivo.
        :returns: :class:`werkzeug.wrappers.Response`, descarga del archivo excel.
        """
        filecontent = base64.b64decode(request.env['project.report.wizard'].browse(int(wizard_id)).report or '')
        return request.make_response(filecontent, [('Content-Type', 'application/excel'),
                                                   ('Content-Disposition', content_disposition(filename))])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

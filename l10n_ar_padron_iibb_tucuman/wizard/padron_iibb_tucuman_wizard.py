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

from datetime import datetime, timedelta
from dateutil import relativedelta
from odoo import models, fields
from odoo.exceptions import ValidationError
import base64, csv, tempfile


def process_file_176(file_to_process):
    """ Procesa el archivo de padron segun rg 176/10"""
    processed_lines = {}
    with open(file_to_process, 'r+') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        # Las primeras 7 líneas del archivo no son datos del padrón, hay una descripción del archivo (ver archivos ej)
        for i in range(7):
            next(reader)
        for row in reader:
            try:
                aliquot = float(row[0][len(row[0]) - 5:len(row[0])])
            except Exception:
                aliquot = 0.0
            try:
                cuit = row[0][:11]
                iibb_type = row[0][16:18]
                date_from = row[0][20:28]
                date_to = row[0][30:38]
                # Si está inscripto en convenio multilateral la alícuota es la mitad
                processed_lines[cuit] = (
                    cuit,
                    date_from,
                    date_to,
                    str(round(float(aliquot) / 2, 5)) if iibb_type == 'CM' else aliquot,
                    iibb_type
                )
            except Exception:
                raise ValidationError("El padrón 176/10 que se quiere procesar contiene un formato inválido.")

    return processed_lines


def process_file_116(file_to_process, processed_lines):
    """ Procesa el archivo de padrón segun RG 116/10, y reemplaza las alícuotas existentes en 176/10 """
    with open(file_to_process, 'r+') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        # Las primeras 5 líneas del archivo no son datos del padrón, hay una descripción del archivo (ver archivos ej)
        for i in range(5):
            next(reader)

        for row in reader:
            try:
                aliquot = float(row[0][len(row[0]) - 5:len(row[0])])
            except Exception:
                aliquot = 0.0
            try:
                base = float(row[0][16:22]) or 1.0
            except Exception:
                base = 1.0
            try:
                cuit = row[0][:11]
                date_val = datetime.strptime(row[0][24:30], '%Y%m')
                date_from = date_val.replace(day=1).strftime('%Y%m%d')
                date_to = ((date_val + relativedelta.relativedelta(months=+1)).replace(day=1) \
                          - timedelta(days=1)).strftime('%Y%m%d')
                line = processed_lines.get(cuit)
                if line:
                    processed_lines[cuit] = (
                        cuit,
                        date_from,
                        date_to,
                        str(round(float(aliquot * base) / 2, 5)) if line and line[4] == 'CM'
                        else round(aliquot * base, 5),
                        line[4] if line else ''
                    )
            except Exception:
                raise ValidationError("El padrón 116/10 que se quiere procesar contiene un formato inválido.")

    return processed_lines


class PadronIIBBTucumanWizard(models.TransientModel):
    _name = 'padron.iibb.tucuman.wizard'
    _description = 'Importación padrón IIBB Tucumán'

    file_176 = fields.Binary(string='Archivo RG 176/10', filename="filename_176", required=True)
    filename_176 = fields.Char(string='Nombre Archivo RG 176/10')
    file_116 = fields.Binary(string='Archivo RG 116/10', filename="filename_116", required=True)
    filename_116 = fields.Char(string='Nombre Archivo RG 116/10')

    def import_padron(self):
        file_176_decoded = base64.b64decode(self.file_176).decode('windows-1251')
        temp_padron_176 = tempfile.NamedTemporaryFile()
        with open(temp_padron_176.name, 'w') as file_padron:
            file_padron.write(file_176_decoded)
            file_padron.seek(0)

        file_116_decoded = base64.b64decode(self.file_116).decode('windows-1251')
        temp_padron_116 = tempfile.NamedTemporaryFile()
        with open(temp_padron_116.name, 'w') as file_padron:
            file_padron.write(file_116_decoded)
            file_padron.seek(0)

        lines = process_file_176(temp_padron_176.name)
        lines = process_file_116(temp_padron_116.name, lines)

        temp_padron_csv = tempfile.NamedTemporaryFile()
        with open(temp_padron_csv.name, 'w') as file_padron_csv:
            csv_out = csv.writer(file_padron_csv)
            for row in lines.keys():
                csv_out.writerow(lines[row])

        # Hacemos el import a la tabla
        try:
            iibb_tucuman_proxy = self.env['padron.iibb.tucuman']
            iibb_tucuman_proxy.truncate_table()
            iibb_tucuman_proxy.action_import(temp_padron_csv.name)
        except Exception:
            raise ValidationError("Hubo un error al procesar el padrón de Tucumán.")
        iibb_tucuman_proxy.massive_update_iibb_tucuman_values()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

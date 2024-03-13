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

from odoo import models, fields
from odoo.exceptions import ValidationError
import os, zipfile, base64, io, glob

PADRON_DELIMITER = ';'
QTY_DELIMITER = 11


class PadronIIBBCABAWizard(models.TransientModel):
    _name = 'padron.iibb.caba.wizard'
    _description = 'Importación padrón IIBB CABA'

    file = fields.Binary(string='Archivo', filename="filename", required=True)
    filename = fields.Char(string='Nombre Archivo')

    @staticmethod
    def _normalize_padron(filepath, newfilepath):
        try:
            with open(filepath, encoding="ISO-8859-1") as oldfile, open(newfilepath, 'w') as newfile:
                for line in oldfile:
                    if line.count(PADRON_DELIMITER) <= QTY_DELIMITER:
                        newfile.write(line)
        except:
            raise ValidationError('Ha ocurrido un error al intentar normalizar el archivo.')

    def import_zip(self):
        """ Importa archivo de IIBB CABA y genera las reglas para los partners correspondientes"""
        padron_caba_path = "/tmp/padron_caba/"
        try:
            import rarfile
        except:
            raise ValidationError("Por favor contáctese con el administrador del "
                                  "sistema para instalar las librerías necesarias ('unrar' (apt) y 'rarfile' (pip)).")
        if self.filename.split(".")[-1].lower() not in ["zip", "rar"]:
            raise ValidationError('Error\nDebe utilizar un archivo ZIP o RAR.')
        # Creo el directorio si no existe
        if not os.path.isdir(padron_caba_path):
            os.mkdir(padron_caba_path)
        file_base = base64.b64decode(self.file)
        file_io = io.BytesIO(file_base)
        if self.filename.split(".")[-1].lower() == "zip":
            try:
                file_ref = zipfile.ZipFile(file_io)
            except:
                raise ValidationError('Error de formato de archivo ZIP')
        else:
            try:
                file_ref = rarfile.RarFile(file_io)
            except:
                raise ValidationError('Error de formato de archivo RAR')

        # Extraigo todos los archivos en el directorio generado
        file_ref.extractall(padron_caba_path)
        file_ref.close()
        # Busco todos los archivos txt dentro del directorio
        files_txt = glob.glob(padron_caba_path + "*.txt")
        if files_txt:
            txt_file = files_txt[0]
            normalize_file_path = '{}.ok'.format(txt_file)
            self._normalize_padron(txt_file, normalize_file_path)
            # Le doy permisos al archivo extraido
            os.chmod(txt_file, 0o777)
            try:
                # Copio los registros del archivo en la tabla
                self.env['padron.iibb.caba'].truncate_table()
                self.env['padron.iibb.caba'].action_import(normalize_file_path)
            except:
                raise ValidationError('Ha ocurrido un error al intentar cargar el padrón. Vuelva a intentarlo.')
        # Elimino archivos
        os.system("rm -r /tmp/padron_caba")

        self.massive_update_iibb_caba_values()

    def massive_update_iibb_caba_values(self):
        self.massive_update_iibb_caba_perceptions()
        self.massive_update_iibb_caba_retentions()

    def massive_update_iibb_caba_perceptions(self):
        """ Actualiza el valor de percepción de IIBB de todos los partners """
        perception = self.env['perception.perception'].get_caba_perception()
        self.env.cr.execute(
            """INSERT into perception_partner_rule (date_from, date_to, percentage, perception_id, partner_id, company_id)
               SELECT
                    to_date(padron_iibb_caba.date_from, 'DDMMYY') as date_from,
                    to_date(padron_iibb_caba.date_to, 'DDMMYY') as date_to,
                    cast(replace(perception_aliquot, ',', '.') as float) as percentage, {perception_id} as perception_id,
                    res_partner.id as partner_id,
                    {company_id} as company_id
                FROM res_partner
                JOIN padron_iibb_caba on res_partner.vat = padron_iibb_caba.cuit and up_down_flag != 'B'
                WHERE res_partner.parent_id is null and res_partner.vat is not null and res_partner.active = True
                ON CONFLICT(perception_id, partner_id, company_id)
                DO UPDATE SET date_from = EXCLUDED.date_from, date_to = EXCLUDED.date_to, percentage = EXCLUDED.percentage"""
                .format(perception_id=perception.id, company_id=perception.company_id.id)
        )
        self.env['perception.partner.rule'].delete_leftover_rules(perception.id, 'padron_iibb_caba')

    def massive_update_iibb_caba_retentions(self):
        """ Actualiza el valor de retención de IIBB de todos los partners """
        retention = self.env['retention.retention'].get_caba_retention()
        self.env.cr.execute(
            """INSERT into retention_partner_rule (date_from, date_to, percentage, retention_id, partner_id, company_id)
               SELECT
                    to_date(padron_iibb_caba.date_from, 'DDMMYY') as date_from,
                    to_date(padron_iibb_caba.date_to, 'DDMMYY') as date_to,
                    cast(replace(retention_aliquot, ',', '.') as float) as percentage, {retention_id} as retention_id,
                    res_partner.id as partner_id,
                    {company_id} as company_id
                FROM res_partner
                JOIN padron_iibb_caba on res_partner.vat = padron_iibb_caba.cuit and up_down_flag != 'B'
                WHERE res_partner.parent_id is null and res_partner.vat is not null and res_partner.active = True
                ON CONFLICT(retention_id, partner_id, company_id)
                DO UPDATE SET date_from = EXCLUDED.date_from, date_to = EXCLUDED.date_to, percentage = EXCLUDED.percentage"""
                .format(retention_id=retention.id, company_id=retention.company_id.id)
        )
        self.env['retention.partner.rule'].delete_leftover_rules(retention.id, 'padron_iibb_caba')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

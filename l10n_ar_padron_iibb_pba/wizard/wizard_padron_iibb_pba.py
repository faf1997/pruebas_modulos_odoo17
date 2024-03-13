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

import os, zipfile
from odoo import models
from odoo.exceptions import ValidationError
from l10n_ar_api.arba_webservices import iibb
from datetime import date


def download_padron(user, password):
    padron = iibb.IIBBPadron(user, password)
    padron_path = padron.get_padron(date.today())
    zip_ref = zipfile.ZipFile(padron_path, 'r')
    path = '/tmp/'
    zip_ref.extractall(path)
    zip_ref.close()
    os.remove(padron_path)
    return [path + ref for ref in zip_ref.namelist()]


class WizardPadronIIBBPba(models.TransientModel):

    _name = 'wizard.padron.iibb.pba'

    def update_padron(self):
        authentication = self.env['arba.webservices.authentication'].get_authentication()
        try:
            names = download_padron(authentication.name, authentication.password)
        except:
            raise ValidationError("No se pudo descargar el padrón, verificar el usuario y contraseña.")

        padron_proxy = self.env['padron.iibb.pba']
        # Actualizamos los padrones y lo borramos del sistema
        padron_proxy.truncate_table()
        padron_proxy.action_import(names[0])
        padron_proxy.action_import(names[1])
        os.remove(names[0])
        os.remove(names[1])
        self.massive_update_iibb_pba_values()

    def massive_update_iibb_pba_values(self):
        self.massive_update_iibb_pba_perceptions()
        self.massive_update_iibb_pba_retentions()

    def massive_update_iibb_pba_perceptions(self):
        """ Actualiza el valor de percepcion de IIBB de todos los partners """
        perception = self.env['perception.perception'].get_iibb_pba_perception()
        self.env.cr.execute(
            """INSERT into perception_partner_rule (date_from, date_to, percentage, perception_id, partner_id, company_id)
               SELECT
                    to_date(padron_iibb_pba.validity_date_since, 'DDMMYY') as date_from,
                    to_date(padron_iibb_pba.validity_date_to, 'DDMMYY') as date_to,
                    cast(replace(aliquot, ',', '.') as float) as percentage, {perception_id} as perception_id,
                    res_partner.id as partner_id,
                    {company_id} as company_id
                FROM res_partner
                JOIN padron_iibb_pba on res_partner.vat = padron_iibb_pba.cuit and padron_iibb_pba.regime = 'P'
                    and up_down_flag != 'B'
                WHERE res_partner.parent_id is null and res_partner.vat is not null and res_partner.active = True
                ON CONFLICT(perception_id, partner_id, company_id)
                DO UPDATE SET date_from = EXCLUDED.date_from, date_to = EXCLUDED.date_to, percentage = EXCLUDED.percentage"""
                .format(perception_id=perception.id, company_id=perception.company_id.id or self.env.company.id)
        )
        self.env['perception.partner.rule'].delete_leftover_rules(perception.id, 'padron_iibb_pba')

    def massive_update_iibb_pba_retentions(self):
        """ Actualiza el valor de percepcion de IIBB de todos los partners """
        retention = self.env['retention.retention'].get_iibb_pba_retention()
        self.env.cr.execute(
            """INSERT into retention_partner_rule (date_from, date_to, percentage, retention_id, partner_id, company_id)
               SELECT
                    to_date(padron_iibb_pba.validity_date_since, 'DDMMYY') as date_from,
                    to_date(padron_iibb_pba.validity_date_to, 'DDMMYY') as date_to,
                    cast(replace(aliquot, ',', '.') as float) as percentage, {retention_id} as retention_id,
                    res_partner.id as partner_id,
                    {company_id} as company_id
                FROM res_partner
                JOIN padron_iibb_pba on res_partner.vat = padron_iibb_pba.cuit and padron_iibb_pba.regime = 'R'
                    and up_down_flag != 'B'
                WHERE res_partner.parent_id is null and res_partner.vat is not null and res_partner.active = True
                ON CONFLICT(retention_id, partner_id, company_id)
                DO UPDATE SET date_from = EXCLUDED.date_from, date_to = EXCLUDED.date_to, percentage = EXCLUDED.percentage"""
                .format(retention_id=retention.id, company_id=retention.company_id.id or self.env.company.id)
        )
        self.env['retention.partner.rule'].delete_leftover_rules(retention.id, 'padron_iibb_pba')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

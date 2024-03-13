# -*- coding: utf-8 -*-
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


class PadronIIBBTucuman(models.Model):
    _name = 'padron.iibb.tucuman'
    _description = 'Línea de padrón IIBB Tucumán'

    cuit = fields.Char(
        'CUIT',
        size=11,
        required=True,
        select=1
    )
    date_from = fields.Char(
        'Validity Date Since',
        size=8,
        required=True
    )
    date_to = fields.Char(
        'Validity Date To',
        size=8,
        required=True
    )
    aliquot = fields.Char(
        'Alícuota',
        size=10,
        required=True
    )
    iibb_type = fields.Char(
        'Tipo de IIBB',
        size=2,
        required=True
    )

    def truncate_table(self):
        self.env.cr.execute("TRUNCATE {} RESTART IDENTITY".format(self._name.replace('.', '_')))

    def action_import(self, file):
        f = open(file, 'r')
        self.env.cr.copy_from(
            f, self._name.replace('.', '_'), sep=',',
            columns=[
                'cuit',
                'date_from',
                'date_to',
                'aliquot',
                'iibb_type'
            ]
        )
        f.close()

    def get_padron_line(self, cuit):
        """ Busca la alícuota para un número de documento"""
        return self.search([('cuit', '=', cuit)], limit=1)

    def massive_update_iibb_tucuman_values(self):
        self.massive_update_iibb_tucuman_perceptions()
        self.massive_update_iibb_tucuman_retentions()

    def massive_update_iibb_tucuman_perceptions(self):
        """ Actualiza el valor de percepción de IIBB de Tucumán de todos los partners """
        perception = self.env['perception.perception'].get_tucuman_perception()
        self.env.cr.execute(
            """INSERT into perception_partner_rule (date_from, date_to, percentage, perception_id, partner_id, company_id)
               SELECT
                    to_date(padron_iibb_tucuman.date_from, 'YYYYMMDD') as date_from,
                    to_date(padron_iibb_tucuman.date_to, 'YYYYMMDD') as date_to,
                    cast(replace(aliquot, ',', '.') as float) as percentage, {perception_id} as perception_id,
                    res_partner.id as partner_id,
                    {company_id} as company_id
                FROM res_partner
                JOIN padron_iibb_tucuman on res_partner.vat = padron_iibb_tucuman.cuit
                WHERE res_partner.parent_id is null and res_partner.vat is not null and res_partner.active = True
                ON CONFLICT(perception_id, partner_id, company_id)
                DO UPDATE SET date_from = EXCLUDED.date_from, date_to = EXCLUDED.date_to, percentage = EXCLUDED.percentage"""
                .format(perception_id=perception.id, company_id=perception.company_id.id)
        )
        self.env['perception.partner.rule'].delete_leftover_rules(perception.id, 'padron_iibb_tucuman')

    def massive_update_iibb_tucuman_retentions(self):
        """ Actualiza el valor de retención de IIBB de Tucumán de todos los partners """
        retention = self.env['retention.retention'].get_tucuman_retention()
        self.env.cr.execute(
            """INSERT into retention_partner_rule (date_from, date_to, percentage, retention_id, partner_id, company_id)
               SELECT
                    to_date(padron_iibb_tucuman.date_from, 'YYYYMMDD') as date_from,
                    to_date(padron_iibb_tucuman.date_to, 'YYYYMMDD') as date_to,
                    cast(replace(aliquot, ',', '.') as float) as percentage, {retention_id} as retention_id,
                    res_partner.id as partner_id,
                    {company_id} as company_id
                FROM res_partner
                JOIN padron_iibb_tucuman on res_partner.vat = padron_iibb_tucuman.cuit
                WHERE res_partner.parent_id is null and res_partner.vat is not null and res_partner.active = True
                ON CONFLICT(retention_id, partner_id, company_id)
                DO UPDATE SET date_from = EXCLUDED.date_from, date_to = EXCLUDED.date_to, percentage = EXCLUDED.percentage"""
                .format(retention_id=retention.id, company_id=retention.company_id.id)
        )
        self.env['retention.partner.rule'].delete_leftover_rules(retention.id, 'padron_iibb_tucuman')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

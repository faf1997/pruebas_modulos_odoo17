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


class PadronIIBBCaba(models.Model):

    _name = 'padron.iibb.caba'
    _description = 'Línea de padrón IIBB CABA'

    name = fields.Char(
        'Razon Social',
        required=True
    )
    publication_date = fields.Char(
        'Publication Date',
        size=8,
        required=True
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
    cuit = fields.Char(
        'CUIT',
        size=11,
        required=True,
        select=1
    )
    contributor_type = fields.Char(
        'Tipo Contribuyente Inscripto',
        size=1
    )
    up_down_flag = fields.Char(
        'Mark Up - Down',
        size=1,
        required=True
    )
    mark_aliquot = fields.Char(
        'Marca alícuota',
        size=1,
        required=True
    )
    perception_aliquot = fields.Char(
        'Alícuota percepción',
        size=4,
        required=True
    )
    retention_aliquot = fields.Char(
        'Alícuota retención',
        size=4,
        required=True
    )
    perception_group_number = fields.Char(
        'Nro grupo percepción',
        size=2,
        required=True
    )
    retention_group_number = fields.Char(
        'Nro grupo retención',
        size=2,
        required=True
    )

    def truncate_table(self):
        self.env.cr.execute("TRUNCATE {} RESTART IDENTITY".format(self._name.replace('.', '_')))

    def action_import(self, path):
        f = open(path, 'r')
        self.env.cr.copy_from(
            f, self._name.replace('.', '_'), sep=';',
            columns=[
                'publication_date',
                'date_from',
                'date_to',
                'cuit',
                'contributor_type',
                'up_down_flag',
                'mark_aliquot',
                'perception_aliquot',
                'retention_aliquot',
                'perception_group_number',
                'retention_group_number',
                'name'
            ]
        )
        f.close()

    def get_padron_line(self, cuit):
        """ Busca la línea para un número de documento"""
        return self.search([('cuit', '=', cuit), ('up_down_flag', '!=', 'B')], limit=1)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

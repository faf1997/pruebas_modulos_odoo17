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


class PadronIIBBPba(models.Model):
    _name = 'padron.iibb.pba'
    _rec_name = 'cuit'

    regime = fields.Char('Regime', size=1, required=True)
    publication_date = fields.Char('Publication Date', size=8, required=True)
    validity_date_since = fields.Char('Validity Date Since', size=8, required=True)
    validity_date_to = fields.Char('Validity Date To', size=8, required=True)
    cuit = fields.Char('CUIT', size=11, required=True, index=1)
    taxpayer_type = fields.Char('Taxpayer Type', size=1, required=True, )
    up_down_flag = fields.Char('Mark Up - Down', size=1, required=True, )
    change_aliquot_flag = fields.Char('Aliquot Changed', size=1, required=True)
    aliquot = fields.Char('Aliquot', size=4, required=True)
    group_number = fields.Char('Group Number', size=2, required=True)
    extra = fields.Char('Extra Content')

    def truncate_table(self):
        self.env.cr.execute("TRUNCATE {} RESTART IDENTITY".format(self._name.replace('.', '_')))

    def action_import(self, path):
        f = open(path, 'r')
        self.env.cr.copy_from(
            f,
            self._name.replace('.', '_'),
            sep=';',
            columns=[
                'regime',
                'publication_date',
                'validity_date_since',
                'validity_date_to',
                'cuit',
                'taxpayer_type',
                'up_down_flag',
                'change_aliquot_flag',
                'aliquot',
                'group_number',
                'extra'
            ]
        )
        f.close()

    def get_retention_padron_line(self, cuit):
        return self.search([('cuit', '=', cuit), ('up_down_flag', '!=', 'B'), ('regime', '=', 'R')], limit=1)

    def get_perception_padron_line(self, cuit):
        return self.search([('cuit', '=', cuit), ('up_down_flag', '!=', 'B'), ('regime', '=', 'P')], limit=1)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

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

from odoo import models


class RetentionPartnerRule(models.Model):
    _inherit = 'retention.partner.rule'

    def delete_leftover_rules(self, retention_id, padron_table):
        """ Elimina las reglas de retenciones de partners que hayan dejado de figurar en un padrón."""

        query = """
            DELETE FROM {table}
            WHERE id IN (
                SELECT rule.id
                FROM {table} rule
                LEFT JOIN res_partner partner ON rule.partner_id = partner.id
                LEFT OUTER JOIN {padron} padron_table ON partner.vat = padron_table.cuit
                WHERE padron_table.cuit IS NULL AND rule.retention_id = %s
            )
        """.format(table=self._table, padron=padron_table)

        self.env.cr.execute(query, (retention_id,))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

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

from odoo.tests.common import TransactionCase
import datetime


class TestPartnerRules(TransactionCase):

    def setUp(self):
        super(TestPartnerRules, self).setUp()

    def test_generar_valores_regla_iibb_caba(self):
        partner = self.env['res.partner'].create({
            'name': 'Test',
            'vat': '111222333'
        })
        self.env['padron.iibb.caba'].create({
            'name': 'TEST',
            'cuit': '111222333',
            'publication_date': '01082018',
            'date_from': '01082018',
            'date_to': '31082018',
            'perception_aliquot': 5.50,
            'retention_aliquot': 1.01,
            'contributor_type': '1',
            'up_down_flag': 'R',
            'mark_aliquot': 'M',
            'perception_group_number': '00',
            'retention_group_number': '00'
        })
        rules = partner.get_rule_values()
        # Percepcion
        assert rules[0][0][2]['percentage'] == 5.50
        assert rules[0][0][2]['date_from'] == datetime.date(2018, 8, 1)
        assert rules[0][0][2]['date_to'] == datetime.date(2018, 8, 31)
        assert rules[0][0][2]['perception_id'] == self.env['perception.perception'].get_caba_perception().id
        # Retencion
        assert rules[1][0][2]['percentage'] == 1.01
        assert rules[1][0][2]['date_from'] == datetime.date(2018, 8, 1)
        assert rules[1][0][2]['date_to'] == datetime.date(2018, 8, 31)
        assert rules[1][0][2]['retention_id'] == self.env['retention.retention'].get_caba_retention().id

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

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


class TestResPartner(TransactionCase):

    def setUp(self):
        super(TestResPartner, self).setUp()

    def test_genero_registros_en_partner(self):
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
        partner.update_rules()
        assert partner.perception_partner_rule_ids
        assert partner.retention_partner_rule_ids

    def test_genero_registros_en_partner_luego_elimino_documento(self):
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
        partner.update_rules()
        assert partner.perception_partner_rule_ids
        assert partner.retention_partner_rule_ids
        partner.write({'vat': ''})
        partner.onchange_vat()
        assert not partner.perception_partner_rule_ids
        assert not partner.retention_partner_rule_ids

    def test_genero_registros_en_partner_luego_de_cargar_documento(self):
        partner = self.env['res.partner'].create({
            'name': 'Test',
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
        partner.update_rules()
        assert not partner.perception_partner_rule_ids
        assert not partner.retention_partner_rule_ids
        partner.write({'vat': '111222333'})
        partner.onchange_vat()
        assert partner.perception_partner_rule_ids
        assert partner.retention_partner_rule_ids

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

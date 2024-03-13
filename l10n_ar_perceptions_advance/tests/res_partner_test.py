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
from odoo.tests.common import TransactionCase


class ResPartnerTest(TransactionCase):

    def setUp(self):
        super(ResPartnerTest, self).setUp()

    def test_delete_lines_onchange_supplier_parent_id(self):
        partner = self.env['res.partner'].create({'name': 'test'})
        self.env['perception.partner.rule'].create({
            'perception_id': self.env.ref('l10n_ar.1_perception_perception_iibb_caba_efectuada').id,
            'percentage': 0,
            'partner_id': partner.id
        })
        partner.onchange_customer_parent_id()
        assert not partner.perception_partner_rule_ids

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

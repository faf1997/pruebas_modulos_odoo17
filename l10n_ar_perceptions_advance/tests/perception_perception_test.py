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
from odoo.exceptions import ValidationError


class PerceptionPerceptionTest(TransactionCase):

    def setUp(self):
        super(PerceptionPerceptionTest, self).setUp()

    def test_gross_income_many_lines(self):
        perception = self.env.ref('l10n_ar.1_perception_perception_iibb_caba_efectuada')
        perception.perception_rule_ids.unlink()
        self.env['perception.perception.rule'].create({
            'perception_id': perception.id,
            'not_applicable_minimum': 0,
            'minimum_tax': 0,
            'percentage': 0,
        })
        self.env['perception.perception.rule'].create({
            'perception_id': perception.id,
            'not_applicable_minimum': 0,
            'minimum_tax': 0,
            'percentage': 0,
        })
        with self.assertRaises(ValidationError):
            perception._check_rules()

    def test_delete_lines_onchange_type_tax_use(self):
        perception = self.env.ref('l10n_ar.1_perception_perception_iibb_caba_efectuada')
        self.env['perception.perception.rule'].create({
            'perception_id': perception.id,
            'not_applicable_minimum': 0,
            'minimum_tax': 0,
            'percentage': 0,
        })
        perception.onchange_type_tax_use()
        assert not perception.perception_rule_ids

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

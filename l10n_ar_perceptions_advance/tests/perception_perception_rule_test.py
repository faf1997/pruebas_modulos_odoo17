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


class PerceptionPerceptionRuleTest(TransactionCase):

    def setUp(self):
        super(PerceptionPerceptionRuleTest, self).setUp()
        self.perception = self.env.ref('l10n_ar.1_perception_perception_iibb_caba_efectuada')

    def test_negative_not_applicable_minimum(self):
        with self.assertRaises(ValidationError):
            self.env['perception.perception.rule'].create({
                'perception_id': self.perception.id,
                'not_applicable_minimum': -1,
                'minimum_tax': 0,
                'percentage': 0,
            })

    def test_negative_minimum_tax(self):
        with self.assertRaises(ValidationError):
            self.env['perception.perception.rule'].create({
                'perception_id': self.perception.id,
                'not_applicable_minimum': 0,
                'minimum_tax': -1,
                'percentage': 0,
            })

    def test_negative_percentage(self):
        with self.assertRaises(ValidationError):
            self.env['perception.perception.rule'].create({
                'perception_id': self.perception.id,
                'not_applicable_minimum': 0,
                'minimum_tax': 0,
                'percentage': -1,
            })

    def test_greater_than_100_percentage(self):
        with self.assertRaises(ValidationError):
            self.env['perception.perception.rule'].create({
                'perception_id': self.perception.id,
                'not_applicable_minimum': 0,
                'minimum_tax': 0,
                'percentage': 101,
            })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

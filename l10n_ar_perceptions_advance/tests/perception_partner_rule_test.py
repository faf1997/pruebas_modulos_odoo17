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


class PerceptionPartnerRuleTest(TransactionCase):

    def setUp(self):
        super(PerceptionPartnerRuleTest, self).setUp()

    def test_constraint_negative_percentage(self):
        rule = self.env['perception.partner.rule'].new({'percentage': -1})
        with self.assertRaises(ValidationError):
            rule._check_percentage()

    def test_constraint_higher_than_100_percentage(self):
        rule = self.env['perception.partner.rule'].new({'percentage': 101})
        with self.assertRaises(ValidationError):
            rule._check_percentage()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

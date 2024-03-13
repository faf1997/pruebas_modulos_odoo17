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


class ResCompanyTest(TransactionCase):

    def test_repeated_line(self):
        self.env['res.company.perception'].search([]).unlink()
        perception = self.env.ref('l10n_ar.1_perception_perception_iibb_caba_efectuada')
        self.env['res.company.perception'].create({
            'company_id': self.env.company_id.id,
            'perception_id': perception.id,
        })
        with self.assertRaises(ValidationError):
            self.env['res.company.perception'].create({
                'company_id': self.env.company_id.id,
                'perception_id': perception.id,
            })

    def setUp(self):
        super(ResCompanyTest, self).setUp()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

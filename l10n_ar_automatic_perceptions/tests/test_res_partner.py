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

from odoo.tests import common
from odoo.exceptions import ValidationError


class TestResPartner(common.TransactionCase):

    def setUp(self):
        super(TestResPartner, self).setUp()

    def test_percepcion_en_partner_y_en_compania(self):
        bs_as = self.env.ref('base.state_ar_b')
        perception = self.env['perception.perception'].new({
            'type': 'gross_income',
            'state_id': bs_as
        })
        company = self.env['res.company'].new({
            'perception_ids': self.env['res.company.perception'].new({
                'perception_id': perception.id
            })
        })
        partner = self.env['res.partner'].new({
            'perception_partner_rule_ids': self.env['perception.partner.rule'].new({
                'perception_id': perception,
                'type': 'gross_income',
                'state_id': bs_as,
                'percentage': 5.0,
            }),
            'company_id': company
        })

        values = partner.get_perceptions_values(None)
        assert values[0] == {perception: 5.0}

    def test_percepcion_en_compania_y_no_en_partner_si_en_factura(self):
        bs_as = self.env.ref('base.state_ar_b')
        perception = self.env['perception.perception'].new({
            'type': 'gross_income',
            'state_id': bs_as,
            'perception_rule_ids': self.env['perception.perception.rule'].new({
                'not_applicable_minimum': 400,
                'percentage': 10
            })
        })
        company = self.env['res.company'].new({
            'perception_ids': self.env['res.company.perception'].new({
                'perception_id': perception.id
            })
        })
        partner = self.env['res.partner'].new({
            'company_id': company,
            'property_account_position_id': self.env.ref('l10n_ar_afip_tables.account_fiscal_position_ivari'),
        })

        values = partner.get_perceptions_values(bs_as)
        assert values[0] == {perception: 10.0}

    def test_percepcion_en_compania_y_no_en_partner_ni_en_factura(self):
        bs_as = self.env.ref('base.state_ar_b')
        perception = self.env['perception.perception'].new({
            'type': 'gross_income',
            'state_id': bs_as
        })
        company = self.env['res.company'].new({
            'perception_ids': self.env['res.company.perception'].new({
                'perception_id': perception.id
            })
        })
        partner = self.env['res.partner'].new({
            'company_id': company,
            'property_account_position_id': self.env.ref('l10n_ar_afip_tables.account_fiscal_position_ivari'),
        })

        with self.assertRaises(ValidationError):
            assert partner.get_perceptions_values(None)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

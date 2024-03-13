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


class TestAccountInvoice(common.TransactionCase):

    def _set_mocks(self):
        self.bs_as = self.env.ref('base.state_ar_b')
        self.tax_21 = self.env.ref('l10n_ar.1_vat_21_ventas')
        self.perception = self.env['perception.perception'].new({
            'type': 'gross_income',
            'state_id': self.bs_as,
            'perception_rule_ids': self.env['perception.perception.rule'].new({
                'not_applicable_minimum': 400,
                'percentage': 10
            })
        })
        self.company = self.env['res.company'].new({
            'perception_ids': self.env['res.company.perception'].new({
                'perception_id': self.perception.id
            })
        })
        self.partner = self.env['res.partner'].new({
            'property_account_position_id': self.env.ref('l10n_ar_afip_tables.account_fiscal_position_ivari'),
            'perception_partner_rule_ids': self.env['perception.partner.rule'].new({
                'perception_id': self.perception,
                'type': 'gross_income',
                'state_id': self.bs_as,
                'percentage': 5.0,
            }),
            'company_id': self.company
        })
        self.product = self.env['product.product'].new({
            'perception_taxable': True
        })
        self.invoice = self.env['account.invoice'].new({
            'partner_id': self.partner,
            'jurisdiction_id': self.bs_as,
            'invoice_line_ids': self.env['account.invoice.line'].new({
                'product_id': self.product,
                'price_subtotal': 1000.0,
                'invoice_line_tax_ids': self.tax_21
            })
        })

    def setUp(self):
        super(TestAccountInvoice, self).setUp()
        self._set_mocks()

    def test_producto_con_iva_21_y_porcentaje_en_cliente_misma_jurisdiccion(self):
        perceptions = self.invoice.get_automatic_perceptions()
        assert perceptions[0]['perception_id'] == self.perception.id
        assert perceptions[0]['base'] == 1000
        assert perceptions[0]['amount'] == 50
        assert perceptions[0]['name'] == self.perception.name
        assert perceptions[0]['jurisdiction'] == self.perception.jurisdiction

    def test_producto_con_iva_21_y_porcentaje_en_cliente_distinta_jurisdiccion_inscripto_en_padron(self):
        perceptions = self.invoice.get_automatic_perceptions()
        self.invoice.jurisdiction_id = self.env.ref('base.state_ar_a')
        assert perceptions[0]['perception_id'] == self.perception.id
        assert perceptions[0]['base'] == 1000
        assert perceptions[0]['amount'] == 50
        assert perceptions[0]['name'] == self.perception.name
        assert perceptions[0]['jurisdiction'] == self.perception.jurisdiction

    def test_producto_con_iva_21_y_porcentaje_en_cliente_distinta_jurisdiccion_no_inscripto_en_padron(self):
        self.invoice.jurisdiction_id = self.env.ref('base.state_ar_a')
        self.partner.perception_partner_rule_ids = None
        assert not self.invoice.get_automatic_perceptions()

    def test_producto_con_iva_21_y_porcentaje_base_misma_jurisdiccion(self):
        self.partner.perception_partner_rule_ids = None
        perceptions = self.invoice.get_automatic_perceptions()
        assert perceptions[0]['perception_id'] == self.perception.id
        assert perceptions[0]['base'] == 1000
        assert perceptions[0]['amount'] == 100
        assert perceptions[0]['name'] == self.perception.name
        assert perceptions[0]['jurisdiction'] == self.perception.jurisdiction

    def test_multiples_producto_con_iva_21_y_porcentaje_en_cliente_misma_jurisdiccion(self):

        invoice = self.env['account.invoice'].new({
            'jurisdiction_id': self.env['res.country.state'].new({}),
            'partner_id': self.partner,
            'invoice_line_ids': self.env['account.invoice.line'].new({
                'product_id': self.product,
                'price_subtotal': 1000.0,
                'invoice_line_tax_ids': self.tax_21
            }) | self.env['account.invoice.line'].new({
                'product_id': self.product,
                'price_subtotal': 2000.0,
                'invoice_line_tax_ids': self.tax_21
            })
        })

        perceptions = invoice.get_automatic_perceptions()
        assert perceptions[0]['perception_id'] == self.perception.id
        assert perceptions[0]['base'] == 3000
        assert perceptions[0]['amount'] == 150
        assert perceptions[0]['name'] == self.perception.name
        assert perceptions[0]['jurisdiction'] == self.perception.jurisdiction

    def test_multiples_productos_con_y_sin_iva_21_y_porcentaje_en_cliente_misma_jurisdiccion(self):
        invoice = self.env['account.invoice'].new({
            'jurisdiction_id': self.env['res.country.state'].new({}),
            'partner_id': self.partner,
            'invoice_line_ids': self.env['account.invoice.line'].new({
                'product_id': self.product,
                'price_subtotal': 1000.0,
                'invoice_line_tax_ids': self.tax_21
            }) | self.env['account.invoice.line'].new({
                'product_id': self.product,
                'price_subtotal': 2000.0,
                'invoice_line_tax_ids': self.env['account.tax'].new({})
            })
        })

        perceptions = invoice.get_automatic_perceptions()
        assert perceptions[0]['perception_id'] == self.perception.id
        assert perceptions[0]['base'] == 1000
        assert perceptions[0]['amount'] == 50
        assert perceptions[0]['name'] == self.perception.name
        assert perceptions[0]['jurisdiction'] == self.perception.jurisdiction

    def test_multiples_productos_distintos_con_cliente_no_inscripto_y_jurisdiccion_en_lugar_de_percepcion(self):
        self.partner.perception_partner_rule_ids = None
        invoice = self.env['account.invoice'].new({
            'partner_id': self.partner,
            'invoice_line_ids': self.env['account.invoice.line'].new({
                'product_id': self.product,
                'price_subtotal': 1000.0,
                'invoice_line_tax_ids': self.tax_21
            }) | self.env['account.invoice.line'].new({
                'product_id': self.product,
                'price_subtotal': 2000.0,
                'invoice_line_tax_ids': self.env['account.tax'].new({'is_exempt': True})
            }),
            'jurisdiction_id': self.bs_as
        })
        perceptions = invoice.get_automatic_perceptions()
        assert perceptions[0]['perception_id'] == self.perception.id
        assert perceptions[0]['base'] == 1000
        assert perceptions[0]['amount'] == 100
        assert perceptions[0]['name'] == self.perception.name
        assert perceptions[0]['jurisdiction'] == self.perception.jurisdiction

    def test_no_supera_el_minimo_no_imponible(self):
        self.invoice.invoice_line_ids = self.env['account.invoice.line'].new({
            'product_id': self.product,
            'price_subtotal': 399.0,
            'invoice_line_tax_ids': self.tax_21
        })

        assert not self.invoice.get_automatic_perceptions()

    def test_producto_que_no_deberia_percibir(self):
        self.product.perception_taxable = False
        assert not self.invoice.get_automatic_perceptions()

    def test_configuracion_inexistente(self):
        self.perception.perception_rule_ids = None
        self.partner.perception_partner_rule_ids = None
        assert not self.invoice.get_automatic_perceptions()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

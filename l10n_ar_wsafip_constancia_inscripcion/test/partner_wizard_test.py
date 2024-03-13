# - coding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
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

from mock import mock
from odoo import SUPERUSER_ID
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from . import config


class PartnerWizardTest(TransactionCase):

    def setUp(self):
        super(PartnerWizardTest, self).setUp()
        self.wsaa = self.env['wsaa.configuration'].create({
            'type': 'homologation',
            'name': 'wsaa',
            'private_key': config.private_key,
            'certificate': config.certificate,
        })
        self.token = self.env['wsaa.token'].create({
            'name': 'ws_sr_padron_a5',
            'wsaa_configuration_id': self.wsaa.id,
        })

        self.user = self.env['res.users'].sudo().browse(SUPERUSER_ID)
        self.user.partner_id.tz = 'America/Argentina/Buenos_Aires'
        self.wizard = self.env['partner.data.get.wizard'].create({
            'vat': 11221233211,
        })
        self.partner = self.env['res.partner'].create({
            'name': 'TEST PARTNER',
            'country_id': self.env.ref('base.ar').id,
            'vat': 20357563276
        })

    def test_get_data_without_configuration(self):
        self.token.unlink()
        with self.assertRaises(ValidationError):
            self.wizard.get_data()

    def test_load_vals(self):

        self.wizard.vat = 30709653543
        # Creamos mocks para simular el comportamiento de AFIP
        data = mock.Mock()
        data.datosGenerales = mock.Mock()
        data.datosGenerales.vat = '30709653543'
        data.datosGenerales.razonSocial = 'Test'

        data.datosGenerales.domicilioFiscal = mock.Mock()
        data.datosGenerales.domicilioFiscal.localidad = 'loc'
        data.datosGenerales.domicilioFiscal.codPostal = '1666'
        data.datosGenerales.domicilioFiscal.direccion = 'Street'
        data.datosGenerales.domicilioFiscal.idProvincia = 1

        vals = self.wizard.load_vals(data)
        assert vals == {
            'name': data.datosGenerales.razonSocial,
            'partner_document_type_id': self.env.ref('l10n_ar_afip_tables.partner_document_type_80').id,
            'vat': data.datosGenerales.vat,
            'country_id': self.env.ref('base.ar').id,
            'state_id': self.env.ref('base.state_ar_b').id,
            'zip': data.datosGenerales.domicilioFiscal.codPostal,
            'city': data.datosGenerales.domicilioFiscal.localidad,
            'street': data.datosGenerales.domicilioFiscal.direccion,
            'property_account_position_id': self.env.ref('l10n_ar_afip_tables.account_fiscal_position_mon').id
        }

    def test_cannot_overwrite_partner(self):
        """No se puede sobreescribir un partner sin tildar 'sobreescribir'"""
        self.wizard.vat = 20357563276

        with self.assertRaises(ValidationError):
            self.wizard.get_and_write_data()

    def test_onchange_partner(self):
        """Testeamos que funciona el onchange"""
        assert self.wizard.vat == '11221233211'

        self.wizard.partner_id = self.partner
        self.wizard.onchange_partner()

        assert self.wizard.vat == '20357563276'

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


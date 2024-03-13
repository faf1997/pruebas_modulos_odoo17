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

{

    'name': 'Cash flow coupon',

    'version': '1.0',

    'category': '',

    'summary': 'Cash flow coupon',

    'author': 'BLUEORANGE GROUP S.R.L',

    'license': 'AGPL-3',

    'website': 'https://www.blueorange.com.ar',

    'depends': [

        'cash_flow',
        'l10n_credit_card_coupon',

    ],

    'data': [

        'views/cash_flow_configuration_view.xml',

    ],

    'installable': True,

    'auto_install': True,

    'application': True,

    'description': """
Cash flow coupon
======================================
* Se agrega posibilidad de agregar cupones al cashflow.
""",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

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

{

    'name': 'L10n ar credit card coupon',

    'version': '1.0.2',

    'category': 'Accounting',

    'summary': 'Cupones de tarjetas de crédito',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'license': 'AGPL-3',

    'website': 'https://www.blueorange.com.ar',

    'depends': [
        'l10n_credit_cards',
        'l10n_treasury',
        'others',
    ],

    'data': [
        'data/ir_rule.xml',
        'views/credit_card.xml',
        'views/credit_card_coupon.xml',
        'views/credit_card_holiday.xml',
        'wizard/credit_card_coupon_closure_wizard_view.xml',
        'security/ir.model.access.csv',
    ],

    'installable': True,

    'auto_install': False,

    'description': """Cupones de tarjetas de crédito""",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

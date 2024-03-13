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

    'name': 'L10n ar credit card installment concile',

    'version': '1.0',

    'category': 'Accounting',

    'summary': 'Conciliación de cuotas de tarjetas de crédito',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'depends': [
        'l10n_credit_card_installment',
    ],

    'data': [
        'data/ir_rule.xml',
        'views/credit_card_installment.xml',
        'views/credit_card_installment_concile.xml',
        'security/ir.model.access.csv',
    ],

    'installable': True,

    'auto_install': False,

    'description': """Conciliación de cuotas de tarjetas de crédito""",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

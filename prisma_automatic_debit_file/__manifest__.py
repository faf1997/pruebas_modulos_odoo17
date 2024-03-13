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

    'name': 'Prisma automatic debit file',

    'version': '1.0',

    'category': 'Accounting',

    'summary': 'Prisma automatic debit file',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'depends': [

        'payment_imputation',
        'prisma_card',
        'others',

    ],

    'data': [

        'security/ir.model.access.csv',
        'views/automatic_debit_file_view.xml',
        'views/account_payment_term_view.xml',
        'wizard/generate_automatic_debit_files_wizard_view.xml',

    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': """Archivos de debito automatico para Prisma""",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

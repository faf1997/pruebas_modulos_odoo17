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

    'name': 'partner_access',

    'version': '1.1',

    'summary': 'Accesos para Partners',

    'description': """En los partner existe la posibilidad de asociar accesos.
    """,

    'author': 'Blueorange Group S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'category': 'others',

    'license': 'AGPL-3',

    'depends': [
        'others',
        'mail',
        'copy_clipboard_extended'
    ],

    'data': [
        'data/ir_module_category.xml',
        'data/res_groups.xml',
        'views/menu.xml',
        'views/res_partner.xml',
        'views/res_partner_access.xml',
        'views/res_partner_access_category.xml',
        'security/ir.model.access.csv'
    ],

    'active': False,

    'installable': True,

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

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

    'name': 'L10n ar arba webservices auth',

    'version': '1.1',

    'category': 'Localization',

    'summary': 'Autenticación para webservices de ARBA',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'license': 'AGPL-3',

    'depends': [
        'l10n_ar_afip_tables',
    ],

    'data': [
        'views/arba_webservices_authentication.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
    ],

    'installable': True,

    'auto_install': False,

    'application': True,

    'description': """Autenticación para webservices de ARBA""",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

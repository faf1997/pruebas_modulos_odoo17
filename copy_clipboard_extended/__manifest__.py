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

    'name': 'copy_clipboard_extended',

    'version': '1.0',

    'category': '',

    'summary': 'Mejoras al widget Clipboard',

    'author': 'BLUEORANGE GROUP S.R.L.',

    'website': 'https://www.blueorange.com.ar',

    'license': 'AGPL-3',

    'depends': [
        'web',
    ],

    'data': [

    ],

    "assets": {
        "web.assets_backend": [
            "copy_clipboard_extended/static/src/js/basic_fields.js",
            "copy_clipboard_extended/static/src/scss/fields.scss"
        ],
    },

    'installable': True,

    'auto_install': False,

    'application': False,

    'description': """Mejoras visuales y funcionales del widget CopyClipboard""",

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

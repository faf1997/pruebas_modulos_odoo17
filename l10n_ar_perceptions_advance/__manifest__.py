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

    "name": "Perceptions Advance",

    "summary": """Percepciones""",

    "description": """Percepciones""",

    "author": "BLUEORANGE GROUP S.R.L.",

    "website": "https://www.blueorange.com.ar",

    "category": "Localization",

    "version": "1.1.1",

    'license': 'AGPL-3',

    "depends": [

        "l10n_ar_perceptions",

    ],

    "data": [

        'security/ir.model.access.csv',
        'views/perception_perception.xml',
        'views/res_partner.xml',
        'views/res_company.xml',
        'data/perception_rules.xml',

    ],

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

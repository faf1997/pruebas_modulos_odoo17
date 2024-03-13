# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import SUPERUSER_ID, api


def migrate(cr, installed_version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref('l10n_ar_arba_webservices_auth.arba_webservices_authentication_multi').domain_force = "['|',('company_id','=',False),('company_id', 'in', company_ids)]"
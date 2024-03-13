# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

def migrate(cr, installed_version):
    cr.execute("update ir_module_module set state = 'to remove' where name = 'l10n_ar_retentions_agip'")

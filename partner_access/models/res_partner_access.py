# -*- encoding: utf-8 -*-
##############################################################################
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import models, fields


class ResPartnerAccess(models.Model):

    _name = 'res.partner.access'

    _inherit = ['mail.thread']

    name = fields.Char(
        string="Descripcion",
        required=True
    )

    application = fields.Char(
        string="Aplicacion",
        tracking=True,
    )

    user = fields.Char(
        string="Usuario",
        tracking=True,
    )

    password = fields.Char(
        string="Password",
        tracking=True,
    )

    host = fields.Char(
        string="Host",
        tracking=True,
    )

    port = fields.Char(
        string="Puerto",
        tracking=True,
    )

    file = fields.Binary(
        string="Archivo",
    )

    filename = fields.Char(
        string="Archivo",
    )

    note = fields.Text(
        string="Nota",
    )

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        required=True
    )

    active = fields.Boolean(
        string="Activo",
        default=True,
    )

    def _default_category(self):
        return self.env['res.partner.access.category'].browse(self._context.get('category_ids'))

    category_ids = fields.Many2many(
        comodel_name='res.partner.access.category',
        column1='access_id',
        column2='category_id',
        string='Categorias',
        default=_default_category
    )

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

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
from odoo.exceptions import ValidationError


class ArbaWerbservicesAuthentication(models.Model):

    _name = 'arba.webservices.authentication'

    name = fields.Char('Usuario', required=True)
    password = fields.Char('Password', required=True)
    sequence = fields.Integer('Prioridad')
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Empresa',
        default=lambda self: self.env.company,
    )

    def get_authentication(self):
        auth = self.search([('company_id', '=', self.env.company.id)], limit=1, order="sequence asc")
        if not auth:
            raise ValidationError("No existe ninguna autenticación para ARBA creada")

        return auth

    _sql_constraints = [('unique_name', 'unique(name)', 'Ya existe una configuracion con ese nombre')]

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

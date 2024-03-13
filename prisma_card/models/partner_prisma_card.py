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

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class PartnerPrismaCard(models.Model):
    _name = 'partner.prisma.card'
    _description = 'Tarjetas para Prisma'

    default_card = fields.Boolean(
        string='Tarjeta por defecto',
        help='Tarjeta por defecto para débito automático.'
    )
    card_number = fields.Char(
        string='Número de tarjeta',
        required=True,
        help='Ingrese el número de tarjeta (16 dígitos) sin espacios.'
    )
    card_type = fields.Selection(
        selection=[
            ('DEBLIQC', 'Visa Crédito'),
            ('DEBLIQD', 'Visa Débito'),
            ('DEBLIMC', 'MasterCard Crédito')
        ],
        string='Tipo',
        required=True
    )
    partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Cliente'
    )

    @api.constrains('card_number', 'card_type', 'partner_id', 'default_card')
    def constraint_card_number(self):
        for card in self:
            if len(card.card_number) != 16 or not card.card_number.isdigit():
                raise ValidationError("El número de tarjeta debe consistir de 16 dígitos.")
            if card.default_card and \
                self.search_count([
                    ('partner_id', '=', card.partner_id.id),
                    ('card_type', '=', card.card_type),
                    ('default_card', '=', True)
                ]) > 1:
                raise ValidationError("Solo puede tener una sola tarjeta del mismo "
                                      "tipo por defecto como débito automático.")
            if self.search_count([
                    ('partner_id', '=', card.partner_id.id),
                    ('card_type', '=', card.card_type),
                    ('card_number', '=', card.card_number)
                ]) > 1:
                raise ValidationError('Ya existe una tarjeta del mismo tipo con el mismo número.')


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

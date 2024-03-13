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


class CreditCardCouponClosureWizard(models.TransientModel):
    _name = 'credit.card.coupon.closure.wizard'
    _description = "Wizard para cierre de cupones de tarjetas de crédito"
    
    closure_date = fields.Date(
        string="Fecha de cierre", 
        default=fields.Date.context_today,
        required=True
    )

    def get_coupon_to_close(self):
        active_ids = self._context.get('active_ids') or self._context.get('active_id')
        coupons_to_close = self.env['credit.card.coupon'].browse(active_ids)
        return coupons_to_close

    def close_coupons(self):
        coupons_to_close = self.get_coupon_to_close()
        for coupon in coupons_to_close:    
            coupon.close(self.closure_date)
        if coupons_to_close:
            return {
                'name': "Cupones cerrados",
                'type': 'ir.actions.act_window',
                'views': [[False, 'list'], [False, 'form']],
                'res_model': 'credit.card.coupon',
                'domain': [['id', 'in', coupons_to_close.ids]],
            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

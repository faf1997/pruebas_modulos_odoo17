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

from l10n_ar_api.documents import tribute


class PerceptionCalculator(object):  # Se encarga de crear la percepcion

    def __init__(self, partner, amount_untaxed, state, company):
        self.partner = partner
        self.amount_untaxed = amount_untaxed
        self.state = state
        self.company = company

    def get_perceptions_values(self):
        perception_values = []
        values = self.partner.get_perceptions_values(self.state, self.company)
        for value in values:
            for perception in value:
                per_vals = self._calculate_perception(perception, value[perception])
                if per_vals:
                    perception_values.append(per_vals)

        return perception_values

    def _calculate_perception(self, perception, percentage):

        minimun_no_aplicable = perception.perception_rule_ids[0].not_applicable_minimum \
            if perception.perception_rule_ids else 0
        minimum_tax = perception.perception_rule_ids[0].minimum_tax \
            if perception.perception_rule_ids else 0
        gross_income = tribute.GrossIncome()
        gross_income.percentage = percentage
        gross_income.minimum_no_aplicable = minimun_no_aplicable
        gross_income.minimum_tax = minimum_tax
        amount = gross_income.calculate_value(self.amount_untaxed)
        if amount[1]:
            return {
                'perception_id': perception.id,
                'aliquot': percentage,
                'base': round(amount[0], 2),
                'amount': round(amount[1], 2),
                'name': perception.name,
                'jurisdiction': perception.jurisdiction
            }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

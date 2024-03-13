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

from ..models import perception_calculator
from mock import mock, MagicMock


class TestPerceptionCalculator(object):

    def test_percepcion_base_1000_5_porciento(self):
        partner = mock.Mock()
        perception = mock.Mock()
        rule = mock.Mock()
        rule.not_applicable_minimum = 400
        perception.id = 1
        perception.name = 'test'
        perception.jurisdiction = 'bs_as'
        perception.perception_rule_ids = [rule]
        r_value = {perception: 5.0}

        partner.get_perceptions_values = MagicMock(return_value=[r_value])
        calculator = perception_calculator.PerceptionCalculator(partner, 1000, None)
        values = calculator.get_perceptions_values()[0]
        assert values['perception_id'] == perception.id
        assert values['base'] == 1000
        assert values['amount'] == 50
        assert values['name'] == perception.name
        assert values['jurisdiction'] == perception.jurisdiction

    def test_percepcion_no_supera_minimo_no_imponible(self):
        partner = mock.Mock()
        perception = mock.Mock()
        rule = mock.Mock()
        rule.not_applicable_minimum = 400
        perception.id = 1
        perception.name = 'test'
        perception.jurisdiction = 'bs_as'
        perception.perception_rule_ids = [rule]
        r_value = {perception: 5.0}

        partner.get_perceptions_values = MagicMock(return_value=[r_value])
        calculator = perception_calculator.PerceptionCalculator(partner, 399, None)
        assert not calculator.get_perceptions_values()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

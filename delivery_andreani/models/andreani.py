import requests
import base64

URL_PROD = "https://apis.andreani.com"
URL_QA = "https://apisqa.andreani.com"


class Andreani:

    def __init__(self, user, password, contract, test=True):
        self.url = URL_QA if test else URL_PROD
        self.user = user
        self.password = password
        self.contract = contract
        self.token = self.authenticate().json().get('token')

    def authenticate(self):
        encoded_auth = base64.b64encode("{}:{}".format(self.user, self.password).encode('UTF-8')).decode('UTF-8')
        res = requests.get(self.url + '/login', headers={"Authorization": "Basic {}".format(encoded_auth)})
        return self._eval_response(res)

    def get_order(self, order_data):
        order_data['contrato'] = self.contract
        res = requests.post(
            self.url + '/v2/ordenes-de-envio',
            headers={'x-authorization-token': self.token},
            json=order_data
        )
        return self._eval_response(res).json()

    def get_shipment(self, shipment_number):
        res = requests.get(
            self.url + '/v2/ordenes-de-envio/{}'.format(shipment_number),
            headers={'x-authorization-token': self.token}
        )
        return self._eval_response(res).json()

    def get_label(self, shipment_number):
        shipment_res = self.get_shipment(shipment_number)
        res = requests.get(
            shipment_res.get('etiquetasPorAgrupador'),
            headers={'x-authorization-token': self.token}
        )
        return self._eval_response(res)

    def _eval_response(self, res):
        if not res.ok:
            raise Exception(res.json().get('detail'))
        return res

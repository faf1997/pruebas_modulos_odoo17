import requests

URL_PROD = "https://ihub.smartkargo.com/ihub-prod-mt-api-function/"
URL_QA = "https://ihub-devtest-mt-apigtw.azure-api.net/ihub-uat-mt-api-function"


class Aerolineas:

    def __init__(self, token, test=True):
        self.url = URL_QA if test else URL_PROD
        self.token = token
        
    def get_book(self, order_data):
        res = requests.post(
            self.url + '/exchange/single',
            headers={'code': self.token},
            json=order_data
        )
        return self._eval_response(res).json()

    def get_label(self, label):
        res = requests.get(
            self.url + "/label?prefix=AXB&airWaybill={}".format(label),
            headers={'code': self.token}
        )
        return self._eval_response(res)

    def _eval_response(self, res):
        if not res.ok:
            raise Exception(res.json().get('detail'))
        # La respuesta puede ser codigo 200, pero haber tenido errores de validacion, en dicho caso
        # se informan de las siguientes dos formas
        if isinstance(res.json(), list) and res.json()[0].get('status') == "Rejected":
            # 1° caso: el error viene informado dentro de los shiptments
            if res.json()[0].get('shipments') and res.json()[0].get('shipments')[0].get('status') == "Rejected":
                raise Exception('.\n'.join([m.get('message') for m in res.json()[0].get('shipments').get('validations', [{}])]))
            # 2° caso: el error viene informado dentro de validations
            elif res.json()[0].get('validations'):
                raise Exception('.\n'.join([m.get('message') for m in res.json()[0].get('validations', [{}])]))   
            else:
                raise Exception("Error de Aerolineas no identificado, por favor comuniquese con el administrador del sistema.")

        return res

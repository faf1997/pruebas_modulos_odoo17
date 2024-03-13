import requests

URL_PROD = "http://epresis-desa.epsared.com.ar" # TODO: Todavia no tengo la URL de produccion
URL_QA = "http://epresis-desa.epsared.com.ar"


class Epsa:

    def __init__(self, token, servicio, sucursal, nombre_etiqueta,test=True):
        self.url = URL_QA if test else URL_PROD
        self.token = token
        self.servicio = servicio
        self.sucursal = sucursal
        self.nombre_etiqueta = nombre_etiqueta
        self.get_api_state()

    def get_api_state(self):
        res = requests.post(
            self.url + '/api/v2/dummy-test.json',
            json={'api_token': self.token}
        )
        return self._eval_response(res).json()

    def get_etiquetas(self, guias):

        res = requests.post(
            self.url + '/api/v2/print-etiquetas-custom',
            json={'api_token': self.token,
                  'tipo': "'fixed'",
                  'nombre': self.nombre_etiqueta,
                  'guias': "{}".format(guias),
                  'ides': "{}".format(guias),
                  'is_remito': 0}
        )
        return self._eval_response(res)

    def _eval_response(self, res):
        if not res.ok:
            raise Exception(res.json().get('message'))
        return res
    
    def post_guia(self, order):
        order.update({
            'api_token': self.token,
            'codigo_servicio': self.servicio,
            'codigo_sucursal': self.sucursal,
        })
        import logging
        log = logging.getLogger(__name__)
        log.info("\n\nMensaje a EPSA {}\n\n".format(order))
        res = requests.post(
            self.url + '/api/v2/guias.json',
            json=order
        )
        return self._eval_response(res).json()
    
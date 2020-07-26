from typing import Union
import json
import sys

from bottle import request, abort, Bottle, ServerAdapter

from tiny_db_client import TinyDBClient


class MyWSGIRefServer(ServerAdapter):
    server = None

    def run(self, *, handler) -> None:
        from wsgiref.simple_server import make_server, WSGIRequestHandler
        if self.quiet:
            class QuietHandler(WSGIRequestHandler):
                def log_request(*args, **kw): pass
            self.options['handler_class'] = QuietHandler
        self.server = make_server(self.host, self.port, handler, **self.options)
        self.server.serve_forever()

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()


class TinyApi:
    def __init__(self, host='localhost', port=8676):
        self.host = host
        self.port = port
        self._api = Bottle()
        self._server = MyWSGIRefServer(port=self.port)
        self._route()

    def _route(self) -> None:
        self._api.route('/create/<database>', method='POST', callback=self._create_doc)
        self._api.route('/read/<database>/<key>/<value>', method='GET', callback=self._read_doc)
        self._api.route('/read/<database>/<key>/<value>/all', method='GET', callback=self._read_doc)
        self._api.route('/update/<database>/<key>/<value>/<update_key>/<update_value>', method='GET',
                        callback=self._update_doc)
        self._api.route('/delete/<database>/<key>/<value>', method='GET', callback=self._delete_doc)
        self._api.route('/stop', method='GET', callback=self.stop)

    def start(self) -> None:
        self._api.run(server=self._server, host=self.host, port=self.port)

    @staticmethod
    def stop() -> None:
        sys.stderr.close()

    @staticmethod
    def _valid_database(*, db: str) -> bool:
        return db in TinyDBClient(database='').list_databases()

    @staticmethod
    def _coerce_int(*, value: str) -> Union[int, str]:
        return int(value) if str(value).isdigit() else value

    def _call_check(self, *, db: str) -> None:
        if not self._valid_database(db=db):
            abort(404, f"Error: Database '{db}' does not exist.")

        if db == TinyDBClient.USERS:
            abort(401, f"Access Denied: Not Authorized to access '{TinyDBClient.USERS}' database.")

    def _create_doc(self, *, database: str) -> dict:
        self._call_check(db=database)
        entry_json = json.loads(request.body.readline())

        for key, value in entry_json.items():
            entry_json[key] = self._coerce_int(value=value)

        result = TinyDBClient(database=database).create_document(document_to_insert=entry_json)
        return result

    def _read_doc(self, *, database: str, key: str, value: str) -> dict:
        self._call_check(db=database)

        result = TinyDBClient(database=database).read_document(
            key=key,
            value=self._coerce_int(value=value),
            return_all=str(request.url).endswith('all')
        )

        return result

    def _update_doc(self, *, database: str, key: str, value: str, update_key: str, update_value: str) -> dict:
        self._call_check(db=database)

        result = TinyDBClient(database=database).update_document(
            key=key,
            value=self._coerce_int(value=value),
            update_key=update_key,
            update_value=self._coerce_int(value=update_value)
        )

        return result

    def _delete_doc(self, *, database: str, key: str, value: str) -> dict:
        self._call_check(db=database)

        result = TinyDBClient(database=database).delete_document(
            key=key,
            value=self._coerce_int(value=value)
        )

        return result


if __name__ == '__main__':
    _api = TinyApi()
    _api.start()

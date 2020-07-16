import json

from bottle import request, abort, Bottle

from tiny_db_client import TinyDBClient


class TinyApi:
    def __init__(self, host='localhost', port=8675):
        self.host = host
        self.port = port
        self._api = Bottle()
        self._route()

    def _route(self) -> None:
        self._api.route('/create/<database>', method='POST', callback=self._create_doc)
        self._api.route('/read/<database>/<key>/<value>', method='GET', callback=self._read_doc)
        self._api.route('/read/<database>/<key>/<value>/all', method='GET', callback=self._read_doc)
        self._api.route('/update/<database>/<key>/<value>/<update_key>/<update_value>', method='GET',
                        callback=self._update_doc)
        self._api.route('/delete/<database>/<key>/<value>', method='GET', callback=self._delete_doc)

    def start(self) -> None:
        self._api.run(host=self.host, port=self.port)

    def _valid_database(self, db):
        return db in TinyDBClient(database='').list_databases()

    def _coerce_int(self, value):
        return int(value) if str(value).isdigit() else value

    def _call_check(self, db):
        if not self._valid_database(db):
            abort(404, f"Error: Database '{db}' does not exist.")

        if db == TinyDBClient.USERS:
            abort(401, f"Access Denied: Not Authorized to access '{TinyDBClient.USERS}' database.")

    def _create_doc(self, database):
        self._call_check(database)
        entry_json = json.loads(request.body.readline())

        for key, value in entry_json.items():
            entry_json[key] = self._coerce_int(value)

        result = TinyDBClient(database=database).create_document(document_to_insert=entry_json)
        return result

    def _read_doc(self, database, key, value):
        self._call_check(database)

        result = TinyDBClient(database=database).read_document(
            key=key,
            value=self._coerce_int(value),
            return_all=str(request.url).endswith('all')
        )

        return result

    def _update_doc(self, database, key, value, update_key, update_value):
        self._call_check(database)

        result = TinyDBClient(database=database).update_document(
            key=key,
            value=self._coerce_int(value),
            update_key=update_key,
            update_value=self._coerce_int(update_value)
        )

        return result

    def _delete_doc(self, database, key, value):
        self._call_check(database)

        result = TinyDBClient(database=database).delete_document(
            key=key,
            value=self._coerce_int(value)
        )

        return result


if __name__ == '__main__':    
    api = TinyApi()
    api.start()

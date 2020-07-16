import json
from typing import List, Dict, Union
import os

from tinydb import TinyDB, Query

from exceptions import DatabaseNotExists


class TinyDBClient:
    DB_PATH = 'data'
    USERS = 'users'
    MULTI_DOC = List[Dict]

    __slots__ = [
        'database'
    ]

    def __init__(self, *, database: str):
        self.database = database

    @property
    def client(self) -> TinyDB:
        if self.database in self.list_databases():
            db = os.path.join(self.DB_PATH, f'{self.database}.json')
            return TinyDB(db, sort_keys=True, indent=4, separators=(',', ': '))
        else:
            raise DatabaseNotExists(f"Database does not exist: {self.database}")

    def _format_response(self, document) -> dict:
        return {'ID': document.doc_id, 'content': document}

    def list_databases(self) -> list:
        return [i.replace('.json', '') for i in os.listdir(self.DB_PATH)]

    def create_document(self, *, document_to_insert: dict) -> dict:
        doc_id = self.client.insert(document_to_insert)
        return {'ID': doc_id}

    def create_multiple_documents(self, *, documents_to_insert: MULTI_DOC) -> dict:
        doc_ids = self.client.insert_multiple(documents_to_insert)
        return {'IDs': doc_ids}

    def read_document(self, return_all=False, *, key: str, value: Union[int, str]) -> dict:
        _query = Query()
        response = self.client.search(_query[key] == value)

        if not return_all:
            _response = self._format_response(response[0])
        else:
            _response = list()
            for doc in response:
                _response.append(self._format_response(doc))

        return {'response': _response}

    def update_document(self, key, value, update_key, update_value):
        _query = Query()
        docs_to_update = self.client.search(_query[key] == value)

        _doc_ids = list()
        for doc in docs_to_update:
            _doc_ids.append(doc.doc_id)
        self.client.update({update_key: update_value}, _query[key] == value)

        result = {'updated_doc_ids': _doc_ids}
        return result

    def delete_document(self, key, value):
        _query = Query()
        docs_to_delete = self.client.search(_query[key] == value)

        _doc_ids = list()
        for doc in docs_to_delete:
            _doc_ids.append(doc.doc_id)
        self.client.remove(_query[key] == value)

        result = {'deleted_doc_ids': _doc_ids}
        return result

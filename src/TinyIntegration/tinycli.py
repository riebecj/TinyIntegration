#!user/bin/python
import subprocess
import argparse
import sys
import os

from tiny_db_client import TinyDBClient


class MongoCli:
    def __init__(self):
        pass

    def _parse_file(self, f):
        if os.path.isfile(f):
            with open(f, 'rt') as data_file:
                json = data_file.read()
                if isinstance(json, dict):
                    return json
                else:
                    try:
                        json = dict(json)
                        return json
                    except:
                        raise ValueError(f'Cannot coerce {json} into dict.')

    def valid_args(self, args):
        operation = args.operation

        if operation == 'create':
            if not args.database:
                print('A database is required.')

            if not args.file:
                print('A file is required when performing create operations\n')
                return False
            return True

        elif operation in ['read', 'delete']:
            if not args.database:
                print('A database is required.')

            if not args.key:
                print('A key is required to perform ', operation, 'operations.\n')
                return False
            if not args.value:
                print('A value is required to perform ', operation, 'operations.\n')
                return False
            return True

        elif operation == 'update':
            if not args.database:
                print('A database is required.')

            if not args.key:
                print('A key is required to perform update operations.\n')
                return False
            if not args.value:
                print('A value is required to perform update operations.\n')
                return False
            if not args.update_key:
                print('An Update Key is required to perform update operations.\n')
                return False
            if not args.update_value:
                print('An Update Value is required to perform update operations.\n')
                return False
            return True

    def main(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-op', '--operation',
                            choices=['create', 'read', 'update', 'delete', 'api-daemon'],
                            required=True,
                            help='The MongoDB Operation to perform.'
                            )
        parser.add_argument('-db', '--database', help='Name of database to use.')
        parser.add_argument('-f', '--file', help='The JSON file used to create a document in the database.')
        parser.add_argument('-k', '--key', help='The key used in read, update, and delete')
        parser.add_argument('-v', '--value', help='The value used in read, update, and delete')
        parser.add_argument('-uk', '--update-key', help='The key to update when updating')
        parser.add_argument('-uv', '--update-value', help='The new value to set the update-key to')
        parser.add_argument('-a', '--all', help='Return all docs on read')
        parser.add_argument('-s', '--start',
                            help='Starts the API daemon',
                            default=False,
                            action='store_true'
                            )
        parser.add_argument('-st', '--stop',
                            help='Stops the API daemon',
                            default=False,
                            action='store_true'
                            )
        parser.add_argument('-r', '--restart',
                            help='Restarts the API daemon',
                            default=False,
                            action='store_true'
                            )

        args = parser.parse_args()
        if args.operation == 'api-daemon':
            print("Starting API")
            subprocess.Popen(
                [
                    'start',
                    f'{sys.executable}',
                    f'{os.path.join(os.path.dirname(os.path.abspath(__file__)), "tiny_api.py")}'
                ],
                shell=True,
            )

        elif not self.valid_args(args):
            parser.print_help()

        else:
            operation = args.operation

            if operation == 'create':
                TinyDBClient(database=args.database).create_document(document_to_insert=self._parse_file(args.file))
            elif operation == 'read':
                TinyDBClient(database=args.database).read_document(key=args.key, value=args.value)
            elif operation == 'delete':
                TinyDBClient(database=args.database).delete_document(key=args.key, value=args.value)
            elif operation == 'update':
                TinyDBClient(database=args.database).update_document(
                    key=args.key,
                    value=args.value,
                    update_key=args.update_key,
                    update_value=args.update_value
                )


if __name__ == '__main__':
    MongoCli().main()

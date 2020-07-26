#!user/bin/python
from getpass import getpass
import subprocess
import argparse
import hashlib
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

        elif operation == 'login' or operation == 'mkuser':
            if not args.username:
                print('A username is required to login.\n')
                return False
            return True

        elif operation == 'create-db' or operation == 'delete-db':
            if not args.database:
                print('A database name is required.\n')
                return False
            return True

    def main(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-op', '--operation',
                            choices=['create', 'read', 'update', 'delete',
                                     'create-db', 'delete-db',
                                     'api-daemon',
                                     'login', 'mkuser'],
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
        parser.add_argument('-s', '--start', help='Starts the API daemon', default=False, action='store_true')
        parser.add_argument('-u', '--username', help='Username for Admin access')
        parser.add_argument('-ad', '--admin', help='make user Admin', default=False, action='store_true')

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

            elif operation == 'mkuser':
                if not self.is_admin():
                    return

                if TinyDBClient(database=TinyDBClient.USERS).user_exists(username=args.username):
                    print(f"Cannot create user {args.username}. User already exists.")
                    return

                while True:
                    password = getpass(f'Please enter password for user {args.username}: ')
                    if password != getpass('Please re-enter password: '):
                        print('Passwords do not match.\n')
                    else:
                        break

                _user = {
                    'username': args.username,
                    'password': self._hash_password(username=args.username, password=password),
                    'role': 'admin' if args.admin else 'user'
                }

                response = TinyDBClient(database=TinyDBClient.USERS).create_document(document_to_insert=_user)
                if response['ID']:
                    print(f"Successfully created user: {args.username}")

            elif operation == 'create-db':
                with open(f'data/{args.database}.json', 'w') as fp:
                    pass
                print(f"Created {args.database} database")

            elif operation == 'delete-db':
                if not self.is_admin():
                    return
                else:
                    os.remove(f'data/{args.database}.json')
                    print(f"Deleted {args.database} database")

    def is_admin(self):
        if not TinyDBClient(database=TinyDBClient.USERS).read_document(key='role', value='admin')['response']:
            self.init_admin()
            return False

        print('You must first login to perform this operation.\n')

        username = input('Enter Username: ')
        password = getpass(f'Please enter password for user {username}: ')

        response = TinyDBClient(database=TinyDBClient.USERS).admin_login(
            username=username,
            password=self._hash_password(username=username, password=password)
        )
        if response:
            print(f'Successfully logged in as {username}')
            return True
        else:
            print('Login failed. Username or Password not correct or user is not Admin.')
            return False

    def init_admin(self):
        print('No admin role exists. Create initial admin role.')
        username = input('Enter Username: ')

        while True:
            password = getpass(f'Please enter password for user {username}: ')
            if password != getpass('Please re-enter password: '):
                print('Passwords do not match.\n')
            else:
                break
        _user = {
            'username': username,
            'password': self._hash_password(username=username, password=password),
            'role': 'admin'
        }
        response = TinyDBClient(database=TinyDBClient.USERS).create_document(document_to_insert=_user)
        if response['ID']:
            print(f"Successfully created user: {username}")

    @staticmethod
    def _hash_password(*, username: str, password: str) -> str:
        _pass = password + username
        hashed_password = hashlib.sha512(_pass.encode()).hexdigest()
        return hashed_password


if __name__ == '__main__':
    MongoCli().main()

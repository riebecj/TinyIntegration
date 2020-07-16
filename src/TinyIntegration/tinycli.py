class MongoCli:
    def __init__(self):
        pass

    def valid_args(self, args):
        operation = args.operation

        if operation == 'create':
            if not args.file:
                print
                'A file is required when performing create operations\n'
                return False
            return True

        elif operation in ['read', 'delete']:
            if not args.key:
                print
                'A key is required to perform ', operation, 'operations.\n'
                return False
            if not args.value:
                print
                'A value is required to perform ', operation, 'operations.\n'
                return False
            return True

        elif operation == 'update':
            if not args.key:
                print
                'A key is required to perform update operations.\n'
                return False
            if not args.value:
                print
                'A value is required to perform update operations.\n'
                return False
            if not args.update_key:
                print
                'An Update Key is required to perform update operations.\n'
                return False
            if not args.update_value:
                print
                'An Update Value is required to perform update operations.\n'
                return False
            return True

    def main(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-op', '--operation', choices=['create', 'read', 'update', 'delete'], required=True,
                            help='The MongoDB Operation to perform.')
        parser.add_argument('-f', '--file', help='The JSON file used to create a document in the database.')
        parser.add_argument('-k', '--key', help='The key used in read, update, and delete')
        parser.add_argument('-v', '--value', help='The value used in read, update, and delete')
        parser.add_argument('-uk', '--update-key', help='The key to update when updating')
        parser.add_argument('-uv', '--update-value', help='The new value to set the update-key to')

        args = parser.parse_args()
        if not self.valid_args(args):
            parser.print_help()
            return
        else:
            operation = args.operation

            if operation == 'create':
                MongoDBClient().create_document(args.file)
            elif operation == 'read':
                MongoDBClient().read_document(args.key, args.value)
            elif operation == 'delete':
                MongoDBClient().delete_document(args.key, args.value)
            else:
                MongoDBClient().update_document(args.key, args.value, args.update_key, args.update_value)


if __name__ == '__main__':
    MongoCli().main()

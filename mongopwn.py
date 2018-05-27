#!/usr/bin/python3

# Author: Hegusung

import argparse
import traceback
import socket
from time import sleep
from datetime import datetime
from ipaddress import IPv4Network
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, OperationFailure


def process(ip, port, timeout, action):
    try:
        client = MongoClient(host=ip, port=port, socketTimeoutMS=timeout*1000, connectTimeoutMS=timeout*1000, serverSelectionTimeoutMS=timeout*1000)

        print("mongodb://%s:%d\tMongoDB %s" % (ip, port, client.server_info()['version']))

        if action == "list_db":
            try:
                for database in client.database_names():
                    print("DB: %s" % database)
                    for collection in client[database].collection_names():
                        print("\t- %s" % collection)
            except OperationFailure:
                print("mongodb://%s:%d Unable to list databases" % (ip, port))

        client.close()

    except socket.timeout:
        pass
    except ServerSelectionTimeoutError:
        pass
    except OSError:
        pass
    except ConnectionRefusedError:
        pass
    except Exception as e:
        traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(description='Tool to exploit Mongo database', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('ip_range', help='ip or ip range', nargs='?', default=None)
    parser.add_argument('-H', help='Host:port file', dest='host_file', default=None)
    parser.add_argument('-p', help='port', dest='port', default=27017, type=int)
    parser.add_argument('-t', help='timeout', nargs='?', default=15, type=int, dest='timeout')
    parser.add_argument('--list-db', help='list databases', action='store_true', dest='list_db')

    args = parser.parse_args()

    port = args.port

    timeout = args.timeout

    if args.list_db:
        action = "list_db"
    else:
        action = None

    if args.ip_range != None:
        for ip in IPv4Network(args.ip_range):
            process(str(ip), port, timeout, action)

    if args.host_file != None:
        with open(args.host_file) as f:
            for line in f:
                host_port = line.split()[0]
                process(host_port.split(":")[0], int(host_port.split(":")[1]), timeout, action)



if __name__ == "__main__":
    main()



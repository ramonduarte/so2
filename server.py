import socket
import sys
import json
import logging
import multiprocessing
from time import sleep
from potvin_rousseau import potvin_rousseau
from google_or_16 import *


log = logging.getLogger("server.log")

def format_solution(solution: list) -> bytes:
    message = json.dumps(solution) + "\n\n"
    return message.encode()


if __name__ == "__main__":
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 8000)
        sock.bind(server_address)
        print('server running on {} port {}'.format(*server_address))

        sock.listen(16)

        while True:
            connection, client_address = sock.accept()
            message_received = b''
            try:
                while True:
                    data = connection.recv(64)
                    message_received += data
                    if message_received.endswith("\n\n".encode()):
                        break

                print(message_received)
                # if data:
                parameters = json.loads(message_received.decode())
                solutions = potvin_rousseau(locations, demands, capacities, time_windows, threads=parameters["threads"])
                print(solutions)
                sleep(10)
                connection.sendall(format_solution(solutions))
                # else:
                #     break
            except Exception as identifier:
                log.error("Server failed: " + str(identifier))
                print("Server failed: " + str(identifier))
                connection.close()
            finally:
                # log.error("Connection closed: " + str(identifier))
                print("Connection closed.")
                # connection.close()
    except Exception as identifier:
        log.error("Connection closed: " + str(identifier))
    finally:
        pass
    

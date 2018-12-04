import socket
import sys
import json
import logging
from potvin_rousseau import potvin_rousseau
from google_or_16 import *


log = logging.getLogger("server.log")

def format_solution(solution: list) -> bytes:
    message = json.dumps(solution) + "\n\n"
    return message.encode()


if __name__ == "__main__":
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 8001)
        sock.bind(server_address)
        print('server running on {} port {}'.format(*server_address))

        sock.listen(16)

        while True:
            connection, client_address = sock.accept()
            try:
                while True:
                    data = connection.recv(64)
                    if data:
                        parameters = json.loads(data.decode())
                        solutions = potvin_rousseau(locations, demands, capacities, threads=parameters["threads"])
                        print(solutions)
                        connection.sendall(format_solution(solutions))
                    else:
                        break
            except Exception as identifier:
                log.error("Server failed: " + str(identifier))
            finally:
                connection.close()
    except Exception as identifier:
        log.error("Connection closed: " + str(identifier))
    finally:
        pass
    

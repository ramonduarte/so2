import socket
import sys
import json
import logging
import multiprocessing
from time import sleep
from potvin_rousseau import potvin_rousseau
import importlib


logging.basicConfig(filename="server.log")


def format_solution(solution: list) -> bytes:
    message = json.dumps(solution) + "\n\n"
    return message.encode()


if __name__ == "__main__":
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 8000)
        sock.bind(server_address)
        print('server running on {} port {}'.format(*server_address))
        logging.info('server running on {} port {}', *server_address)

        sock.listen(16)
        connection, client_address = sock.accept()

        while True:
            sleep(1)
            message_received = b''
            try:
                logging.info('ready to receive packets')
                while True:
                    data = connection.recv(128)
                    message_received += data
                    if message_received.endswith("\n\n".encode()):
                        break

                logging.info(message_received)
                if message_received == "\n\n".encode():
                    continue
                parameters = json.loads(message_received.decode()[:-2])

                graph = importlib.import_module(parameters["infile"])
                locations = graph.locations
                demands = graph.demands
                capacities = graph.capacities
                name = graph.name
                time_windows = graph.time_windows

                # real-time changes to the graph
                ## number of customers
                if parameters["n"] and parameters["n"]  > len(locations) - 1:
                    connection.sendall("Not enough capacity to support more customers.\n\n".encode())
                    continue
                ## demands
                if parameters["demands"]:
                    aux = demands[:]
                    for c in parameters["demands"]:
                        demands[c[0]] = c[1]
                    if sum(demands) > sum(capacities):
                        connection.sendall("Not enough capacity to support this demand.\n\n".encode())
                        demands = aux[:]
                        continue
                ## locations
                if parameters["locations"]:
                    for c in parameters["locations"]:
                        locations[c[0]] = c[1]
                ## capacities
                if parameters["capacities"]:
                    aux = capacities[:]
                    for c in parameters["capacities"]:
                        capacities[c[0]] = c[1]
                    if sum(demands) > sum(capacities):
                        connection.sendall("Not enough capacity to support current demand.\n\n".encode())
                        capacities = aux[:]
                        continue
                ## number of vehicles
                if parameters["k"] and parameters["k"] < len(capacities) - 1:
                    connection.sendall("Not enough vehicles to fill in routes.\n\n".encode())
                    continue
                
                n = parameters["n"] + 1 if parameters["n"] else len(demands) - 1
                k = parameters["k"] if parameters["k"] else len(capacities)

                [solutions, speedup] = potvin_rousseau(
                    locations[:n],
                    demands[:n],
                    capacities + (k - len(capacities))*[max(capacities)],
                    time_windows[:n],
                    threads=parameters["threads"])
                connection.sendall(format_solution(solutions))

                # saving last graph
                with open("last_graph.py", "w") as last_graph:
                    last_graph.writelines([
                        "name = '" + name + "'\n",
                        "locations = " + json.dumps(locations) + "\n",
                        "demands = " + json.dumps(demands) + "\n",
                        "capacities = " + json.dumps(capacities) + "\n",
                        "time_windows = " + json.dumps(time_windows) + "\n",
                        "speedup = " + str(speedup) + "\n"
                    ])

            except Exception as identifier:
                print("Server failed: " + repr(identifier))
                logging.error("Server failed: " + repr(identifier))
                logging.error("Connection closed.")
                print("Connection closed.")
            finally:
                pass
    except Exception as identifier:
        logging.error("Connection closed: " + repr(identifier))
        print("Connection closed: " + repr(identifier))
    finally:
        pass


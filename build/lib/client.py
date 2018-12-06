import socket
import sys
import click
import json
import logging
import multiprocessing
import cmd
import asyncio
import signal
from time import sleep

logging.basicConfig(filename="client.log")
exit_flag = False
message = {}
sock = None
solutions = []

class Prompt(cmd.Cmd):
    prompt = "client> "

    def do_exit(self, inp):
        print("Closing application...")
        global exit_flag
        exit_flag = True
        return True

    def do_commands(self, inp):
        print(
            """
            Commands available in interactive mode:
            commands                             Show list of commands available in interactive mode.
            customers <int>                      Change number of customers.
            demands [[<int>, <int>]]             Change demands of customers.
            locations [[<int>, [<int>, <int>]]]  Change location of customers.
            capacities [[<int>, <int>]]          Change capacity of vehicles.
            vehicles <int>                       Change number of vehicles.
            update                               Retrieve last run from socked.
            examples                             Show list of examples.
            """
        )
        return True

    def do_examples(self, inp):
        print(
            """
            Some examples:
            customers 15                         Reduce graph to at most 15 customers.
            demands [[15, 6], [7, 5]]            Change demand of customers 15 and 7 to 6 and 5, respectively (0 is not a customer).
            locations [[1, [0,0]], [12, [8,5]]]  Change location of customers 1 and 12 to [x=0, y=0] and [x=8, y=5], respectively (on a 2D planar graph).
            capacities [[0, 18], [1, 25]]        Change capacity of trucks 0 and 1 to 18 and 25, respectively.
            vehicles 5                           Change number of vehicles to at most 5.
            """
        )
        return True

    def do_customers(self, inp):
        # example: customers 15
        global message, sock
        message["n"] = int(inp)
        sock.sendall((json.dumps(message) + "\n\n").encode())
        return True

    def do_demands(self, inp):
        # example: demands [[15, 6], [7, 5]]
        global message, sock
        demands = json.loads(inp)
        message["demands"] = demands
        sock.sendall((json.dumps(message) + "\n\n").encode())
        return True
        
    def do_locations(self, inp):
        # example: locations [[1, [0,0]], [12, [8,5]]]
        global message, sock
        locations = json.loads(inp)
        message["locations"] = locations
        sock.sendall((json.dumps(message) + "\n\n").encode())
        return True
        
    def do_capacities(self, inp):
        # example: capacities [[0, 18], [1, 25]]
        global message, sock
        capacities = json.loads(inp)
        message["capacities"] = capacities
        sock.sendall((json.dumps(message) + "\n\n").encode())
        return True
        
    def do_vehicles(self, inp):
        # example: vehicles 5
        global message, sock
        message["k"] = int(inp)
        sock.sendall((json.dumps(message) + "\n\n").encode())
        return True
        
    def do_update(self, inp):
        message_received = b""
        while True:
            data = sock.recv(128)
            message_received += data
            if message_received.endswith("\n\n".encode()):
                break
        print(message_received.decode())
        
        solutions = json.loads(message_received.decode())
        if type(solutions) == type(" "):
            print("message: " + solutions)
            return True
        
        i = 0
        j = 0
        for solution in solutions:
            i += 1
            print("solution " + str(i))
            for route in solution:
                j += 1
                print("\troute " + str(j))
                for key, value in route.items():
                    print("\t\t" + key + " : " + str(value))
            j = 0

        return True

    do_EOF = do_exit

    def postloop(self):
        try:
            sleep(2)
            message_received = b""
            while True:
                data = sock.recv(128)
                message_received += data
                if message_received.endswith("\n\n".encode()):
                    break

            solutions = json.loads(message_received.decode()[:-2])
            if type(solutions) == type(" "):
                print("message: " + solutions)
                return True

            i = 0
            j = 0
            for solution in solutions:
                i += 1
                print("solution " + str(i))
                for route in solution:
                    j += 1
                    print("\troute " + str(j))
                    for key, value in route.items():
                        print("\t\t" + key + " : " + str(value))
                j = 0
            

            sock.sendall("\n\n".encode())
        except:
            pass
        finally:
            return True


def echo_cmd():
    while True:
        inp = input("Write something: ")

        print(inp)

@click.command()
@click.option('--threads', '-t', default=1, help='Number of parallel executions.')
@click.option('--infile', '-i', default="google_or_16", help='Filename to input graph.')
@click.option('--outfile', '-o', default=None, help='Filename to write output.')
def hello(threads, infile, outfile):
    click.echo('Running Potvin-Rousseau CVRPTW algorithm with ' + str(threads) + " threads.")

    global message, solutions
    message = {
        "threads": threads,
        "infile": infile,
        ## n -> int  =>  graph becomes n-graph
        "n": None,
        ## demands -> list([customer, demand])  =>  G.nodes[customer]["demand"] = demand
        "demands": None,
        ## locations -> list([customer, tuple(x, y)])  =>  G.nodes[customer]["location"] = tuple
        "locations": None,
        ## capacities -> list([truck, capacity])  =>  capacities[truck] = capacity
        "capacities": None,
        ## k -> int  =>  len(capacities) = k
        "k": None,
    }
    sock.sendall((json.dumps(message) + "\n\n").encode())

    message_received = b''

    while not exit_flag:
        try:
            pool = multiprocessing.Pool(processes=2)
            pmt = Prompt()
            pool.apply_async(pmt.cmdloop())
            pool.get(60)

            while True:
                data = sock.recv(128)
                message_received += data

                if message_received.endswith("\n\n".encode()):
                    break
            print(message_received.decode())
            solutions = json.loads(message_received.decode())
        except:
            sleep(1)
        finally:

            if type(solutions) == type(" "):
                print("message: " + solutions)

            elif outfile:
                with open(outfile, 'w') as o:
                    i = 0
                    j = 0
                    for solution in solutions:
                        i += 1
                        o.write("solution " + str(i) + "\n")
                        for route in solution:
                            j += 1
                            o.write("\troute " + str(j) + "\n")
                            for key, value in route.items():
                                o.write("\t\t" + key + " : " + str(value) + "\n")
                        j = 0

    print('closing socket')
    logging.warning('closing socket')
    sock.close()


if __name__ == "__main__":
    sock = socket.create_connection(('localhost', 8000))
    sleep(2)
    while True:
        try:
            hello()
        except Exception as identifier:
            logging.error("Client failed: " + repr(identifier))
            print("Client failed: " + repr(identifier))
            break
        finally:
            logging.info("Restarting client...")
            # break
    

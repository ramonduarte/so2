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

log = logging.getLogger("client.log")
exit_flag = False
message = {}

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
            commands               Show list of commands available in interactive mode.
            customers                 Show list of commands available in interactive mode.
            add                    Show list of commands available in interactive mode.
            change                 Show list of commands available in interactive mode.
            """
        )
        return True

    def do_customers(self, inp):
        # example: customers 12
        global message
        message["n"] = int(inp)

        sock.sendall((json.dumps(message) + "\n\n").encode())
        print(message)
        return True

    def do_demands(self, inp):
        # example: demands [[15, 6], [7, 5]]
        global message
        demands = json.loads(inp)
        message["demands"] = demands

        sock.sendall((json.dumps(message) + "\n\n").encode())
        print(message)
        return True
        
    def do_locations(self, inp):
        # example: locations [[1, (0,0)], [12, (8,5)]]
        global message
        locations = json.loads(inp)
        message["locations"] = locations
        
        sock.sendall((json.dumps(message) + "\n\n").encode())
        print(message)
        return True
        
    def do_capacities(self, inp):
        # example: capacities [[0, 18], [1, 25]]
        global message
        capacities = json.loads(inp)
        message["capacities"] = capacities

        sock.sendall((json.dumps(message) + "\n\n").encode())
        print(message)
        return True
        
    def do_vehicles(self, inp):
        # example: vehicles 5
        global message
        message["k"] = int(inp)
        
        sock.sendall((json.dumps(message) + "\n\n").encode())
        print(message)
        return True

    do_EOF = do_exit


def handler(sig, frame):
    return


def echo_cmd():
    while True:
        inp = input("Write something: ")

        print(inp)

@click.command()
@click.option('--threads', '-t', default=1, help='Number of parallel executions.')
@click.option('--infile', '-i', default="google_or_16", help='Filename to input graph.')
@click.option('--outfile', '-o', default=None, help='Filename to write output.')
@click.option('--demo', '-d', default=False, help='Set to True for a slower execution to illustrate functionality.')
def hello(threads, infile, outfile, demo):
    click.echo('Running Potvin-Rousseau CVRPTW algorithm with ' + str(threads) + " threads.")

    sock = socket.create_connection(('localhost', 8000))

    # Quick protocol
    ## n -> int  =>  graph becomes n-graph
    ## demands -> list([customer, demand])  =>  G.nodes[customer]["demand"] = demand
    ## locations -> list([customer, tuple(x, y)])  =>  G.nodes[customer]["location"] = tuple
    ## capacities -> list([truck, capacity])  =>  capacities[truck] = capacity
    ## k -> int  =>  len(capacities) = k
    global message
    message = {
        "threads": threads,
        "infile": infile,
        "demo": demo,
        "n": None,
        "demands": None,
        "locations": None,
        "capacities": None,
        "k": None,
    }
    sock.sendall((json.dumps(message) + "\n\n").encode())
    print(message)

    # Look for the response
    # amount_received = 0
    # amount_expected = len(message)
    message_received = b''

    pool = multiprocessing.Pool(processes=2)
    #     # CLI interface must have its own thread
    #     # interface = multiprocessing.Process(target=hello)

        # real-time features run silently after interface initialized
        # pool.apply_async(hello)
    print("While you wait")
    pmt = Prompt()
        # pool.apply_async(pmt.cmdloop())
    try:
        while not exit_flag:
            pool.apply_async(pmt.cmdloop())

            data = sock.recv(64)
            message_received += data

            if message_received.endswith("\n\n".encode()):
                break
    except:
        pass
    finally:
        while True:
            data = sock.recv(64)
            message_received += data

            if message_received.endswith("\n\n".encode()):
                break

        


    # while True:
        # data = sock.recv(64)
        # message_received += data

        # if message_received.endswith("\n\n".encode()):
        #     break

    # finally:

    pool.close()
    pool.join()
    message = message_received.decode()[:-2]
    solutions = json.loads(message)
    print(solutions)

    if outfile:
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

    # await asyncio.sleep(10)
    print('closing socket')
    sock.close()


# Create a TCP/IP socket
# sock = socket.create_connection(('localhost', 8000))

if __name__ == "__main__":
    while True:
        try:
            # CLI interface must have its own thread
            # interface = multiprocessing.Process(target=hello)
            # interface = multiprocessing.Process(target=hello)
            # loop = asyncio.get_event_loop()
            # task = loop.create_task(hello())
            # loop.run_until_complete(task)
            # print("While you wait")
            # cmd = multiprocessing.Process(target=Prompt.cmdloop)


            # CLI interface must have its own thread
            # interface = multiprocessing.Process(target=hello)
            # interface = multiprocessing.Process(target=hello)
            # loop = asyncio.get_event_loop()
            # task = loop.create_task(hello())
            # loop.run_until_complete(task)
            # print("While you wait")
            # cmd = multiprocessing.Process(target=Prompt.cmdloop)

            # real-time features run silently after interface initialized
            # print("While you wait")
            # # for p in (interface, cmd):
            # #     p.start()

            # with multiprocessing.Pool(processes=2) as pool:
            #     # CLI interface must have its own thread
            #     # interface = multiprocessing.Process(target=hello)

            #     # real-time features run silently after interface initialized
            #     pool.apply_async(hello)
            #     print("While you wait")
            # pmt = Prompt()
            # pmt.cmdloop()
                # pool.apply(pmt.cmdloop)
            hello()
        except Exception as identifier:
            log.error("Client failed: " + str(identifier))
        finally:
            # log.info("Restarting client...")
            break
    

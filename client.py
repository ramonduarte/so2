import socket
import sys
import click
import json
import logging

log = logging.getLogger("client.log")


@click.command()
@click.option('--threads', '-t', default=1, help='Number of parallel executions.')
@click.option('--infile', '-i', default="google_or_16", help='Filename to input graph.')
@click.option('--outfile', '-o', default=None, help='Filename to write output.')
@click.option('--demo', '-d', default=False, help='Set to True for a slower execution to illustrate functionality.')
def hello(threads, infile, outfile, demo):
    click.echo('Running Potvin-Rousseau CVRPTW algorithm with ' + str(threads) + "threads.")

    sock = socket.create_connection(('localhost', 8001))
    message = {
        "threads": threads,
        "infile": infile,
        "demo": demo
    }
    sock.sendall(json.dumps(message).encode())

    # Look for the response
    # amount_received = 0
    # amount_expected = len(message)
    message_received = b''

    while True:
        data = sock.recv(64)
        message_received += data

        if message_received.endswith("\n\n".encode()):
            break

    # finally:

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

    print('closing socket')
    sock.close()

# Create a TCP/IP socket
# sock = socket.create_connection(('localhost', 8000))

if __name__ == "__main__":
    while True:
        try:
            hello()
        except Exception as identifier:
            log.error("Client failed: " + str(identifier))
        finally:
            # log.info("Restarting client...")
            break
    

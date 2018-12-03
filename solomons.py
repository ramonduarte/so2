
import networkx as nx
import matplotlib.pyplot as plt
import math
import itertools
import logging
import argparse
from sys import argv
from functools import partial
from multiprocessing import Pool, Array, current_process, Queue
from timeit import default_timer as timer
from google_or_12 import *

log = logging.getLogger("solomons.log")

def powerset(iterable, lb=1):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(lb, len(s)+1))

def weight(node1: [float,float], node2: [float,float]):
    return math.sqrt((node1[0]-node2[0])**2
                      + (node1[1]-node2[1])**2)

def total_distance(G, route):
    dist = G.get_edge_data(0, route[0][0])["weight"] + G.get_edge_data(0, route[0][-1])["weight"]
    for i in range(len(route[0]) - 1):
        dist += G.get_edge_data(route[0][i], route[0][i+1])["weight"]
    return dist or 2 * G.get_edge_data(0, route[0])["weight"]


def solomons(locations, demands, capacities, time_windows=None):
    G = nx.Graph(instance=name)
    # start = timer()
    solution = []

    for i in range(len(locations)):
        G.add_node(i, location=locations[i], demand=demands[i], status=0)

    for i in range(len(locations)):
        for j in range(len(locations)):
            if i >= j:
                continue
            G.add_edge(i, j,
                    weight=math.sqrt(
                        (locations[i][0]-locations[j][0])**2
                            + (locations[i][1]-locations[j][1])**2))

    total_demand = sum(demands)

    # TODO: add some bullshit calculations 2018-12-01 22:10:32

    for truck in capacities:
        # find nearest unattended customer
        current_node = 0
        nearest_neighbor = None
        min_distance = 9999999999
        min_weight = 9999999999
        furthest_neighbor = None
        max_distance = 0

        route = {"path": [0], "weight": 0, "demand": 0, "surplus": truck}
        
        print("New route: depot ", end="=> ")
        
        for customer in range(1, len(locations)):
            if G.node[customer]["status"]:
                continue
            if current_node == customer:
                continue
            if max_distance < G.get_edge_data(current_node, customer)["weight"]:
                max_distance = G.get_edge_data(current_node, customer)["weight"]
                furthest_neighbor = customer
        current_node = furthest_neighbor
        if current_node == None or truck < 0:
                break
        truck -= G.node[current_node]["demand"]
        G.node[current_node]["status"] = 1
        
        while truck > 0:
            print("{:>3}".format(current_node), end=" => ")
            current_node_demand = G.node[current_node]["demand"]

            if route["path"][-1] != current_node:
                route["path"].append(current_node)
                # route["weight"] += min_distance
                route["demand"] += current_node_demand
            for customer in range(1, len(locations)):
                if G.node[customer]["status"] or current_node == customer:
                    continue
                if min_distance > G.get_edge_data(current_node, customer)["weight"]:
                    min_distance = G.get_edge_data(current_node, customer)["weight"]
                    nearest_neighbor = customer
            current_node = nearest_neighbor
            if current_node == None:
                break
            truck -= G.node[current_node]["demand"]
            route["surplus"] = truck if truck >= 0 else truck + G.node[current_node]["demand"]
            if truck < 0:
                break
            if route["path"][-1] != current_node:
                route["path"].append(current_node)
                route["weight"] += min_distance
                route["demand"] += current_node_demand
            G.node[current_node]["status"] = 1
            # print("(capacity left {})".format(truck), end=" ")
            min_distance = 9999999999

        print("{:>3} and back to depot".format(current_node))
        try:
            this_solution_distance = sum([G.get_edge_data(route["path"][x],
                                      route["path"][x+1])["weight"]
                                      for x in range(len(route["path"]) - 1)]) \
                                      + G.get_edge_data(route["path"][-1], 0)["weight"] \
                                      + G.get_edge_data(route["path"][1], 0)["weight"]
            print("weight: {}".format(this_solution_distance))
        except:
            print(route)
            pass
        
        route["weight"] += G.get_edge_data(route["path"][-1], 0)["weight"] \
                              + G.get_edge_data(route["path"][1], 0)["weight"]
        route["demand"] += current_node_demand
        route["path"].append(0)
        solution.append(route)

    # print(solution, end="\n\n")

    global rotas
    rotas.put([current_process()._identity[0] - 1, solution])
    # print("\n\n****", rotas, end="\n\n")

    return solution


def potvin_rousseau(locations, demands, capacities, time_windows=None):
    # TODO: add some bullshit code here 2018-12-01 22:09:20
    return


print(argv)
number_of_threads = int(argv[1]) if len(argv) > 1 else 4

arguments = argparse.ArgumentParser()
arguments.add_argument(
  "--locations",
  nargs="*",
  type=int,
  default=locations,
)
arguments.add_argument(
  "--demands",
  nargs="*",
  type=int,
  default=demands,
)
arguments.add_argument(
  "--capacities",
  nargs="*",
  type=int,
  default=capacities,
)
arguments.add_argument(
  "--time_windows",
  nargs="*",
  type=int,
  default=None,
)
parsed_args = arguments.parse_args()


rotas = Queue()
def init(q):
    global rotas
    rotas = q


pt = partial(solomons,
             demands=parsed_args.demands,
             capacities=parsed_args.capacities)
with Pool(number_of_threads, initializer=init, initargs=(rotas,)) as p:
    p.map(pt, [parsed_args.locations]*number_of_threads)
    p.close()
    p.join()

while not rotas.empty():
    print(rotas.get())
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
from time import sleep

from google_or_16 import *

log = logging.getLogger("potvin_rousseau.log")

def powerset(iterable, lb=1):
    "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
    s = list(iterable)
    return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(lb, len(s)+1))

def weight(node1: [float,float], node2: [float,float]):
    return math.sqrt((node1[0]-node2[0])**2
                      + (node1[1]-node2[1])**2)

def total_distance(G, route):
    return sum([G.get_edge_data(route[i], route[i+1])["weight"] for i in range(len(route)-1)])

def total_demand(G, route):
    return sum([G.node[i]["demand"] for i in route])

def total_service_time(G, route):
    raise NotImplementedError


def solomons(locations, demands, capacities, time_windows=None):
    G = nx.Graph(instance=name)
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

    for truck in capacities:
        # find nearest unattended customer
        current_node = 0
        nearest_neighbor = None
        min_distance = 9999999999
        # min_weight = 9999999999
        furthest_neighbor = None
        max_distance = 0

        route = {"path": [0], "weight": 0, "demand": 0, "surplus": truck}
        
        # print("New route: depot ", end="=> ")
        
        for customer in range(1, len(locations)):
            if G.node[customer]["status"] or current_node == customer:
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
            # print("{:>3}".format(current_node), end=" => ")
            current_node_demand = G.nodes[current_node]["demand"]

            if route["path"][-1] != current_node:
                route["path"].append(current_node)
                # route["weight"] += min_distance
#                 route["demand"] += current_node_demand
                # print("demand1 = {}, current_node_demand = {}".format(route["demand"], current_node_demand))
            for customer in range(1, len(locations)):
                if G.node[customer]["status"] or current_node == customer:
                    continue
                if min_distance > G.get_edge_data(current_node, customer)["weight"]:
                    min_distance = G.get_edge_data(current_node, customer)["weight"]
                    nearest_neighbor = customer
            current_node = nearest_neighbor
            if current_node == None:
                break
            truck -= G.nodes[current_node]["demand"]
            route["surplus"] = truck if truck >= 0 else truck + G.nodes[current_node]["demand"]
            if truck < 0:
                break
            if route["path"][-1] != current_node:
                route["path"].append(current_node)
                route["weight"] += min_distance
                route["demand"] += current_node_demand
                
            G.node[current_node]["status"] = 1
            min_distance = 9999999999

        # print("{:>3} and back to depot".format(current_node))
        try:
            this_solution_distance = sum([G.get_edge_data(route["path"][x],
                                      route["path"][x+1])["weight"]
                                      for x in range(len(route["path"]) - 1)]) \
                                      + G.get_edge_data(route["path"][-1], 0)["weight"] \
                                      + G.get_edge_data(route["path"][1], 0)["weight"]
            # print("weight: {}".format(this_solution_distance))
        except:
            # print(route)
            pass
        
        route["weight"] += G.get_edge_data(route["path"][-1], 0)["weight"] \
                              + G.get_edge_data(route["path"][1], 0)["weight"]
        route["demand"] += current_node_demand
        
        route["path"].append(0)
        solution.append(route)


#     global rotas
#     rotas.put([current_process()._identity[0] - 1, solution])
    # print("\n\n****", rotas, end="\n\n")

    return solution

from random import randint

def build_routes(parameters: tuple, capacities: list, seeds: list, g: nx.Graph):
    G = nx.Graph(g)  # do not change graph in place
    solution = []
    
    assert len(seeds) == len(capacities)
    assert sum(parameters) == 1.0
    
    c = 0
    for s in seeds:
        solution += [{
            "path": [0, s, 0],
            "weight": total_distance(G, [0, s, 0]),
            "demand": total_demand(G, [0, s, 0]),
            "surplus": capacities[c] - total_demand(G, [0, s, 0])}]
        c += 1
        G.node[s]["status"] = 1
    
#     best_insertions = []
    customer_list = sorted(list(G.nodes), key=lambda x: -G.node[x]['demand'])
    # print(customer_list)

    for customer in customer_list:
        min_cost = 99999999999
        best_insertions = []
        best_path = []
        # print(customer)
        # G,nodes is unhashable & depot is not a customer
        if customer != 0 and not G.node[customer]["status"]:  # True if already routed
            for route in solution:
                if G.node[customer]["demand"] <= route["surplus"]:
                    for node in range(len(route["path"]) - 2):
                        if customer not in route["path"]:
                            cost = (
                                total_distance(G, [route["path"][node], customer, route["path"][node+1]]) * parameters[0]
                                # TODO: change it to total service time, not total distance
                                + total_distance(G, [route["path"][node+1], customer, route["path"][node+1]]) * parameters[1]
                                # + total_service_time(G, [route["path"][node+1], customer, route["path"][node+1]]) * parameters[1]
                            )
                            # print(route["path"], " cost = ", cost, " min cost = ", min_cost)
                            if min_cost > cost:
                                # print(route["path"][:node+1], customer, route["path"][node+1:])
                                min_cost = cost
                                best_path = route["path"][:node+1] + [customer] + route["path"][node+1:]
                                assert best_path != []

                    best_insertions.append({
                        "path": best_path,
                        "cost": min_cost
                    })

                    # print((customer not in (route["path"])), (G.node[route["path"][node]]["demand"] <= route["surplus"]))

                    assert route["surplus"] >= 0
                else:
                    best_insertions.append({
                            "path": False,
                            "cost": 0
                        })

            # print(best_insertions)
            # TODO: check if this is the right iteration (customer instead of while True)
            max_obj = 99999999999
            insertion_with_max_obj = None
            for insertion in range(len(best_insertions)):
                if best_insertions[insertion]["path"]:
                    obj = best_insertions[insertion]["cost"] * (len(best_insertions) - 1)
                    for insertion2 in best_insertions:
                        if best_insertions[insertion] != insertion2:
                            obj -= insertion2["cost"]

                    if max_obj > obj:
                        # print("max obj = ", max_obj, " obj = ", obj)
                        max_obj = obj
                        insertion_with_max_obj = insertion

            # TODO: check if this route is within time_windows


            # insert customer
            # TODO: index() is terribly slow

            assert best_insertions[insertion_with_max_obj]["path"]

            if capacities[insertion_with_max_obj] - total_demand(G, best_insertions[insertion_with_max_obj]["path"]) >= 0:
                solution[insertion_with_max_obj] = {
                    "path": best_insertions[insertion_with_max_obj]["path"],
                    "weight": total_distance(G, best_insertions[insertion_with_max_obj]["path"]),
                    "demand": total_demand(G, best_insertions[insertion_with_max_obj]["path"]),
                    "surplus": capacities[insertion_with_max_obj] - total_demand(G, best_insertions[insertion_with_max_obj]["path"])
                }

            # print([i for x in solution for i in x["path"]])
            assert customer in [i for x in solution for i in x["path"]]

        G.node[customer]["status"] = 1

    # sleep(60)
    return solution
        

def potvin_rousseau(locations, demands, capacities, time_windows, name="instance", threads=1):
    # STEP 1: how many vehicles are needed?
    solomons_result = solomons(locations, demands, capacities, time_windows)
    # k = len(solomons_result)  # number of vehicles
    starting_nodes = [x["path"][1] for x in solomons_result]

    # building graph
    G = nx.Graph(instance=name)

    for i in range(len(locations)):
        G.add_node(i, location=locations[i], demand=demands[i], time_windows=time_windows[i], status=0)

    for i in range(len(locations)):
        for j in range(len(locations)):
            if i >= j:
                continue
            G.add_edge(i, j,
                    weight=math.sqrt(
                        (locations[i][0]-locations[j][0])**2
                            + (locations[i][1]-locations[j][1])**2))
    
    solomons_parameters = [(0.5, 0.5), (0.75, 0.25), (1.0, 0.0), (0.6, 0.4),
                           (0.525, 0.475), (0.725, 0.275), (0.95, 0.05), (0.625, 0.375),
                           (0.55, 0.45), (0.775, 0.225), (0.9, 0.1), (0.65, 0.35),
                           (0.575, 0.425), (0.8, 0.2), (0.85, 0.15), (0.675, 0.325),]
    solutions = []

    pt = partial(build_routes,
             capacities=capacities,
             seeds=starting_nodes,
             g=G)

    # multithreaded execution
    with Pool(threads) as t:
        solutions = t.map(pt, solomons_parameters[:threads])
        
        # force faster threads to wait
        t.close()
        t.join()
    
    return solutions

if __name__ == "__main__":
    potvin_rousseau(locations, demands, capacities, time_windows, threads=3)


# rotas = Queue()
# def init(q):
#     global rotas
#     rotas = q



# with Pool(number_of_threads, initializer=init, initargs=(rotas,)) as p:
#     p.map(pt, [parsed_args.locations]*number_of_threads)
#     p.close()
#     p.join()

# while not rotas.empty():
#     print(rotas.get())
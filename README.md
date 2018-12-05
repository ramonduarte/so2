# A client-server Python implementation of the Potvin-Rousseau heuristic algorithm to the CVRPTW

## 1. Inspiration

This project was done as a requirement to the **_EEL770 Operating Systems_** course, part of the Computer & Information Engineering program at UFRJ.

## 2. Usage examples

### 2.1 Shell commands

 - Options:
 
>  `-t, --threads INTEGER  Number of parallel executions.`

>  `-i, --infile TEXT      Filename to input graph.`
 
>  `-o, --outfile TEXT     Filename to write output.`

>  `--help                 Show this message and exit.`

### 2.2 Real-time parameter tweaking

 - Commands available in interactive mode:

> `commands                             Show list of commands available in interactive mode.`

> `customers <int>                      Change number of customers.`

> `demands [[<int>, <int>]]             Change demands of customers.`

> `locations [[<int>, [<int>, <int>]]]  Change location of customers.`

> `capacities [[<int>, <int>]]          Change capacity of vehicles.`

> `vehicles <int>                       Change number of vehicles.`

> `update                               Retrieve last run from socked.`

> `examples                             Show list of examples.`

>  `-t, --threads INTEGER  Number of parallel executions.`

>  `-i, --infile TEXT      Filename to input graph.`
 
>  `-o, --outfile TEXT     Filename to write output.`

>  `--help                 Show this message and exit.`

### 2.3 Tests with `google_or_16.py` preloaded graph

> `customers 15`

> `demands [[15, 6], [7, 5]]`

> `locations [[1, [0,0]], [12, [8,5]]]`

> `capacities [[0, 18], [1, 25]]`

> `vehicles 5`


## 3. Implementation details

### 3.1 Server (`server.py`)

 - Must be run first. By default, it opens a TCP socket at `localhost:8000`.
 - Responsible to compute the algorithm, but does not start until receiving the necessary parameters.
 - Parallelism is achieved by the `multiprocessing` native module and `Queue` lock-based data structure.
 - Calculates _speedup_ between parallel and sequential executions.
 - Logging & recovery file writing through `logging`.

### 3.2 Client (`client.py`)

 - Can be run by either `python client.py [OPTIONS]` or installed through `python setup.py install` and then run by `client [OPTIONS]`.
 - Provides CLI interface through `click` and `cmd` libraries.
 - Interacts in real-time with the server through the TCP socket.
 - Handles parameter tweaking through shell commands.

### Algorithm (`potvwin_rousseau.py`)

 - An heuristic, parallel approach to the Capacitated Vehicle Routing Problem with Time Windows, as described by Potvin & Rousseau (1990).
 - Deploys a relaxation approach based on two parameters (demand-based and time-based, respectively) that can be set on runtime and easily consolidated through thread `join()`.
 - Graph data structure provided by the `networkx` package.

## 4 References

1. DANTZIG, George B.; RAMSER, John H. The truck dispatching problem. Management science, v. 6, n. 1, p. 80-91, 1959.

2. TOTH, Paolo; VIGO, Daniele. An overview of vehicle routing problems. In: The vehicle routing problem. Society for Industrial and Applied Mathematics, 2002. p. 1-26.

3. POTVIN, Jean-Yves; ROUSSEAU, Jean-Marc. A parallel route building algorithm for the vehicle routing and scheduling problem with time windows. European Journal of Operational Research, v. 66, n. 3, p. 331-340, 1993.
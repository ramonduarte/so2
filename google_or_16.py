# Google OR CVRP Example

name = "Google OR CVRP Example (n=16)"

# Locations in block units
locations = \
      [(4, 4), # depot
       (2, 0), (8, 0), # locations to visit
       (0, 1), (1, 1),
       (5, 2), (7, 2),
       (3, 3), (6, 3),
       (5, 5), (8, 5),
       (1, 6), (2, 6),
       (3, 7), (6, 7),
       (0, 8), (7, 8)]

demands = [0, # depot
         1, 1, # row 0
         2, 4,
         2, 4,
         8, 8,
         1, 2,
         1, 2,
         4, 4,
         8, 8]

capacities = [15, 15, 15, 15]

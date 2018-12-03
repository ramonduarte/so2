# Google OR CVRP Example

name = "Google OR CVRP Example (n=16)"

# Locations in block units
locations = \
      [(4, 4), # depot
       (2, 0), (8, 0), # locations to visit
       (3, 0), (7, 0),
       (3, 1), (7, 1),
       (0, 1), (1, 1),
       (5, 2), (7, 2),
       (3, 3), (6, 3),
       (5, 5), (8, 5),
       (1, 6), (2, 6),
       (3, 7), (6, 7),
       (2, 7), (7, 7),
       (0, 8), (7, 8),
       (1, 8), (5, 8)]

demands = [0, # depot
         1, 1, # row 0
         16, 16,
         2, 4,
         32, 32,
         2, 4,
         8, 8,
         1, 2,
         1, 2,
         4, 4,
         32, 32,
         8, 8,
         16, 16]

capacities = [63, 63, 63, 63]

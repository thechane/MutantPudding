#credit - http://www.redblobgames.com/pathfinding/a-star/introduction.html, http://www.redblobgames.com/pathfinding/a-star/implementation.html

import collections
import heapq
from Brains.Hexagon import *
from Brains.HexagonRoot import *

class Astar(object):

    def __init__(self, **kwargs):
        pass

    def heuristic(self, a, b):
        (x1, y1) = a
        (x2, y2) = b
        return abs(x1 - x2) + abs(y1 - y2)

    def a_star_search(self, graph, start, goal):
        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0

        while not frontier.empty():
            current = frontier.get()

            if current == goal:
                break

            for next in graph.neighbors(current):
                new_cost = cost_so_far[current] + graph.cost(current, next)
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + heuristic(goal, next)
                    frontier.put(next, priority)
                    came_from[next] = current

        return came_from, cost_so_far


class HexGrid:
    def __init__(self, coord_labels, cubeIndex, reachableCubes):
        self.reachableCubes = reachableCubes
        self.weights = {}
        for cube in reachableCubes:
            self.weights[cube] = coord_labels[ cubeIndex[cube.ID] ].weight

    def neighbors(self, cube):
        results = []
        for dirIndex in range(0, 6):
            neighbor = cube.Neighbor(dirIndex)
            if neighbor in self.reachableCubes:
                results.append(neighbor)
        return results

    def cost(self, from_node, to_node):
        return self.weights.get(from_node) + self.weights.get(to_node)

class PriorityQueue:
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]

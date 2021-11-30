import heapq


class PriorityQueue:
    def __init__(self):
        self.pq = []

    def add(self, el, priority):
        heapq.heappush(self.pq, (priority, el))

    def pop(self):
        _, el = heapq.heappop(self.pq)
        return el

    def is_empty(self):
        return len(self.pq) == 0


class Node:
    def __init__(self, state, get_childs):
        self.state = discrete_state(*state)
        self.get_childs = get_childs

    @property
    def children(self):
        return self.get_childs(self.state)

    def __eq__(self, other):
        return self.state == other.state

    def __hash__(self):
        return str(self.state)


class AstarSearch:
    def __init__(self, metric, heuristic, get_next_states):
        self.metric = metric
        self.heuristic = heuristic
        self.get_next_states = get_next_states

    def build_trajectory(self, start, target):
        start_node = self.to_node(start)
        target_node = self.to_node(target)
        trajectory = self.search(start_node, target_node)
        return trajectory

    def search(self, start_node, target_node):
        que = PriorityQueue()
        que.add(start_node, 0)
        parents = {start_node: None}
        cost = {start_node: 0}

        while not que.is_empty():
            current_node = que.pop()
            if current_node == target_node:
                break

            for child_node in current_node.children:
                child_cost = cost[current_node] + self.metric(child_node.state, current_node.state)
                if child_node not in cost or child_cost < cost[child_node]:
                    cost[child_node] = child_cost
                    priority = child_cost + self.heuristic(child_node.state)
                    parents[child_node] = current_node
                    que.add(child_node, priority)

        trajectory = self.restore_trajectory(parents, target_node)
        return trajectory

    @staticmethod
    def restore_trajectory(parents, current_node):
        node_trajectory = []
        while current_node:
            node_trajectory.append(current_node)
            current_node = parents[current_node]
        return list(reversed(node_trajectory))

    def to_node(self, state):
        state = Node(state, self.get_next_states)
        return state


def discrete_state(x, y, yaw):
    return round(x), round(y), round(yaw)

__version__ = "0.4.0"
from collections.abc import Mapping
from .graph import Graph, Vertex
from .exceptions import RepeatedTransition, FutureTransition, StatusNotFound, TransitionNotFound


class StatusMap(Mapping):
    def __init__(self, transitions):
        graph = Graph()
        graph.add_nodes(*transitions.keys())
        for node in graph.get_nodes():
            to_nodes = transitions[node]
            graph.add_edges_from_node(node, to_nodes)

        self.graph = graph

    def __repr__(self):
        return f"StatusMap(statuses={self.statuses})"

    def __getitem__(self, key):
        if isinstance(key, Vertex):
            key = key.name
        return self.graph.get_node(key)

    def __len__(self):
        return self.graph.num_nodes

    def __iter__(self):
        return iter(graph)

    @property
    def statuses(self):
        return tuple(self.graph.get_nodes())

    def _validate_status_exists(self, from_status, to_status):
        if from_status not in self.graph.get_nodes():
            raise StatusNotFound(f"from_status {from_status} not found")

        if to_status not in self.graph.get_nodes():
            raise StatusNotFound(f"to_status {to_status} not found")

    def _validate_invalid_transition(self, from_status, to_status, distances):
        if distances[(from_status, to_status)] == 0 and distances[(to_status, from_status)] == 0:
            msg = f"transition from {from_status} to {to_status} not found"
            raise TransitionNotFound(msg)

    def _validate_is_previous(self, from_status, to_status, distances):
        if distances[(from_status, to_status)] == 0:
            msg = f"transition from {from_status} to {to_status} should have happened in the past"
            raise RepeatedTransition(msg)

    def _validate_is_future(self, from_status, to_status, distances):
        if distances[(from_status, to_status)] > 1:
            msg = f"transition from {from_status} to {to_status} should happen in the future"
            raise FutureTransition(msg)

    def validate_transition(self, from_status, to_status):
        self._validate_status_exists(from_status, to_status)

        distances = self.graph.get_relative_distances(from_status, to_status)
        if from_status != to_status:
            self._validate_invalid_transition(from_status, to_status, distances)
            self._validate_is_previous(from_status, to_status, distances)
            self._validate_is_future(from_status, to_status, distances)

from typing import Dict, Any
import networkx as nx

class Gate:
    def __init__(self, id: str, type: str, position=(0,0)):
        self.id = id
        self.type = type.upper()
        self.inputs = []
        self.value = None
        self.position = position
        if self.type == "NOT":
            self.inputs = ["a"]
        elif self.type in ("AND", "OR", "NAND", "NOR", "XOR"):
            self.inputs = ["a","b"]
        elif self.type == "INPUT":
            self.inputs = []
        elif self.type == "OUTPUT":
            self.inputs = ["a"]
        else:
            self.inputs = []

    def eval(self, input_values: Dict[str, bool]) -> bool:
        t = self.type
        if t == "INPUT":
            return bool(self.value)
        if t == "OUTPUT":
            return bool(input_values.get("a", False))
        a = bool(input_values.get("a", False))
        b = bool(input_values.get("b", False))
        if t == "AND":
            return a and b
        if t == "OR":
            return a or b
        if t == "NAND":
            return not (a and b)
        if t == "NOR":
            return not (a or b)
        if t == "XOR":
            return a ^ b
        if t == "NOT":
            return not a
        return False

class Circuit:
    def __init__(self):
        self.G = nx.DiGraph()
        self.gates = {}

    def add_gate(self, gate: Gate):
        self.gates[gate.id] = gate
        self.G.add_node(gate.id)

    def remove_gate(self, gid: str):
        if gid in self.gates:
            del self.gates[gid]
        if gid in self.G:
            self.G.remove_node(gid)

    def connect(self, src_id: str, dst_id: str, dst_pin: str = "a"):
        if src_id not in self.gates or dst_id not in self.gates:
            raise ValueError("Gate id not found")
        self.G.add_edge(src_id, dst_id, pin=dst_pin)

    def disconnect(self, src_id: str, dst_id: str):
        if self.G.has_edge(src_id, dst_id):
            self.G.remove_edge(src_id, dst_id)

    def set_input_value(self, input_id: str, value: bool):
        g = self.gates.get(input_id)
        if g and g.type == "INPUT":
            g.value = bool(value)
        else:
            raise ValueError("Not an input gate")

    def evaluate(self) -> Dict[str, Any]:
        if not nx.is_directed_acyclic_graph(self.G):
            cycles = list(nx.simple_cycles(self.G.to_directed()))
            raise RuntimeError(f"Cycle detected in circuit: {cycles}")

        order = list(nx.topological_sort(self.G))
        values = {}
        for gid in order:
            gate = self.gates[gid]
            in_edges = list(self.G.in_edges(gid, data=True))
            pin_vals = {}
            for (src, _, data) in in_edges:
                pin = data.get("pin", "a")
                pin_vals[pin] = bool(values.get(src, False))
            try:
                result = gate.eval(pin_vals)
            except Exception:
                result = False
            values[gid] = bool(result)
        for gid, gate in self.gates.items():
            if gid not in values:
                if gate.type == "INPUT":
                    values[gid] = bool(gate.value)
                else:
                    values[gid] = False
        return values

    def clear(self):
        self.G.clear()
        self.gates.clear()

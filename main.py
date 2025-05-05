import simpy
import yaml
import random
from collections import defaultdict

def load_config(path):
    with open(path) as f:
        cfg = yaml.safe_load(f)
    return cfg['queues'], cfg['max_clients']

class QueueNode:
    def __init__(self, env, name, servers, capacity, arr_params, svc_params, routes, stats, max_clients, sim_end):
        self.env = env
        self.name = name
        self.servers = servers
        self.resource = simpy.Resource(env, capacity=servers)
        self.capacity = capacity
        self.arr_low, self.arr_high = arr_params
        self.svc_low, self.svc_high = svc_params
        self.routes = routes
        self.stats = stats
        self.max_clients = max_clients
        self.sim_end = sim_end

        self.occupancy = 0
        self.state_times = defaultdict(float)
        self.last_event_time = env.now
        self.last_occupancy = 0

        if self.arr_low is not None:
            env.process(self.arrival_generator())

    def record_state_change(self):
        now = self.env.now
        duration = now - self.last_event_time
        self.state_times[self.last_occupancy] += duration
        self.last_event_time = now
        self.last_occupancy = self.occupancy

    def arrival_generator(self):
        while self.stats['arrivals'] < self.max_clients:
            ia = random.uniform(self.arr_low, self.arr_high)
            yield self.env.timeout(ia)
            cid = self.stats['next_id']
            self.stats['next_id'] += 1
            self.stats['arrivals'] += 1
            self.env.process(self.process_customer(cid, self.env.now))

    def process_customer(self, cid, start_time):
        occupied = self.occupancy
        if self.capacity is not None and occupied >= self.capacity:
            self.stats['lost'] += 1
            self.stats[f'lost_{self.name}'] += 1
            self.stats['finished'] += 1
            self.stats['response_time_sum'] += (self.env.now - start_time)
            if self.stats['finished'] >= self.max_clients:
                self.sim_end.succeed()
            return

        self.record_state_change()
        self.occupancy += 1
        self.record_state_change()

        with self.resource.request() as req:
            yield req
            svc = random.uniform(self.svc_low, self.svc_high)
            yield self.env.timeout(svc)

        self.record_state_change()
        self.occupancy -= 1
        self.record_state_change()

        r = random.random()
        cum = 0.0
        next_hop = 'exit'
        for dest, p in self.routes.items():
            cum += p
            if r <= cum:
                next_hop = dest
                break

        if next_hop == 'exit':
            self.stats['completed'] += 1
            self.stats['response_time_sum'] += (self.env.now - start_time)
            self.stats['finished'] += 1
            if self.stats['finished'] >= self.max_clients:
                self.sim_end.succeed()
        else:
            yield self.env.process(
                self.env.queues[next_hop].process_customer(cid, start_time)
            )


def main():
    queues_cfg, max_clients = load_config("config.yml")
    env = simpy.Environment()
    stats = defaultdict(int)
    stats.update({
        'next_id': 1,
        'arrivals': 0,
        'completed': 0,
        'lost': 0,
        'finished': 0,
        'response_time_sum': 0.0
    })

    for q in queues_cfg:
        stats[f'lost_{q["name"]}'] = 0

    sim_end = env.event()

    env.queues = {}
    for q in queues_cfg:
        name = q['name']
        servers = q['servers']
        capacity = q.get('capacity', None)
        arr = q.get('arrival')
        arr_params = (arr['low'], arr['high']) if arr else (None, None)
        svc = q['service']
        svc_params = (svc['low'], svc['high'])
        routes = q['routes']
        env.queues[name] = QueueNode(
            env, name, servers, capacity,
            arr_params, svc_params, routes,
            stats, max_clients, sim_end
        )

    env.run(until=sim_end)

    print(f"Tempo total: {env.now:.4f}")

    for name, node in env.queues.items():
        print(f"\n\n{name}: ({stats[f'lost_{name}']} clientes perdidos)")
        print(f"Estado  |     Tempo     |   Probabilidade  ")
        print(f"--------------------------------------")
        for occupancy, t in sorted(node.state_times.items()):
            if t <= 0:
                continue
            prob = t / env.now
            print(f"   {occupancy}    |   {t:.4f}   |   {prob:.4f}")

if __name__ == "__main__":
    main()

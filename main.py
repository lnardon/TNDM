import random
import heapq
import math

class QueueSimulation:
    def __init__(self, num_servers, max_queue_size, arrival_min, arrival_max, service_min, service_max, simulation_time):
        self.num_servers = num_servers
        self.max_queue_size = max_queue_size
        self.arrival_min = arrival_min
        self.arrival_max = arrival_max
        self.service_min = service_min
        self.service_max = service_max
        self.simulation_time = simulation_time
        self.current_time = 0
        self.event_queue = []
        self.queue = []
        self.servers_busy = 0
        self.state_times = [0] * (max_queue_size + 1)
        self.last_state_change_time = 0
        self.total_customers = 0
        self.dropped_customers = 0

    def generate_random_time(self, min_val, max_val):
        return random.uniform(min_val, max_val)

    def schedule_arrival(self):
        arrival_time = self.current_time + self.generate_random_time(self.arrival_min, self.arrival_max)
        heapq.heappush(self.event_queue, (arrival_time, 'A'))

    def schedule_departure(self, server_index=None):
        service_time = self.generate_random_time(self.service_min, self.service_max)
        departure_time = self.current_time + service_time
        heapq.heappush(self.event_queue, (departure_time, 'D', server_index))

    def handle_arrival(self):
        self.update_state_time()
        self.total_customers += 1

        if self.servers_busy < self.num_servers:
            self.servers_busy += 1
            self.schedule_departure()
        elif len(self.queue) < self.max_queue_size:
            self.queue.append(self.current_time)
        else:
            self.dropped_customers += 1
        self.schedule_arrival()

    def handle_departure(self, server_index=None):
        self.update_state_time()
        self.servers_busy -= 1

        if self.queue:
            self.queue.pop(0)
            self.schedule_departure()
        
    def update_state_time(self):
        state_time = self.current_time - self.last_state_change_time
        self.state_times[len(self.queue)] += state_time
        self.last_state_change_time = self.current_time

    def run_simulation(self):
        self.schedule_arrival()

        while self.event_queue and self.current_time < self.simulation_time:
            event_time, event_type, *args = heapq.heappop(self.event_queue)
            self.current_time = event_time

            if event_type == 'A':
                self.handle_arrival()
            elif event_type == 'D':
                self.handle_departure(*args)

        total_sim_time = self.current_time
        state_probabilities = [state_time / total_sim_time for state_time in self.state_times]

        return {
            'total_customers': self.total_customers,
            'dropped_customers': self.dropped_customers,
            'total_simulation_time': total_sim_time,
            'state_times': self.state_times,
            'state_probabilities': state_probabilities
        }

def simulate_queue(num_servers, max_queue_size, arrival_min, arrival_max, service_min, service_max, simulation_time=100000):
    sim = QueueSimulation(
        num_servers=num_servers, 
        max_queue_size=max_queue_size, 
        arrival_min=arrival_min, 
        arrival_max=arrival_max, 
        service_min=service_min, 
        service_max=service_max, 
        simulation_time=simulation_time
    )
    return sim.run_simulation()

def main():
    print("Simulação G/G/1/5:")
    g1_result = simulate_queue(
        num_servers=1, 
        max_queue_size=5, 
        arrival_min=2, 
        arrival_max=5, 
        service_min=3, 
        service_max=5
    )
    print("\n--- Resultados para G/G/1/5 ---")
    print(f"Tempo Global da Simulação: {g1_result['total_simulation_time']:.2f}")
    print(f"Total de Clientes: {g1_result['total_customers']}")
    print(f"Clientes Perdidos: {g1_result['dropped_customers']}")
    
    print("\nDistribuição de Probabilidades dos Estados da Fila:")
    for estado, probabilidade in enumerate(g1_result['state_probabilities']):
        print(f"Estado {estado}: {probabilidade:.4f}")
    
    print("\nTempos Acumulados por Estado:")
    for estado, tempo in enumerate(g1_result['state_times']):
        print(f"Estado {estado}: {tempo:.2f}")
    
    print("\n\nSimulação G/G/2/5:")
    g2_result = simulate_queue(
        num_servers=2, 
        max_queue_size=5, 
        arrival_min=2, 
        arrival_max=5, 
        service_min=3, 
        service_max=5
    )
    print("\n--- Resultados para G/G/2/5 ---")
    print(f"Tempo Global da Simulação: {g2_result['total_simulation_time']:.2f}")
    print(f"Total de Clientes: {g2_result['total_customers']}")
    print(f"Clientes Perdidos: {g2_result['dropped_customers']}")
    
    print("\nDistribuição de Probabilidades dos Estados da Fila:")
    for estado, probabilidade in enumerate(g2_result['state_probabilities']):
        print(f"Estado {estado}: {probabilidade:.4f}")
    
    print("\nTempos Acumulados por Estado:")
    for estado, tempo in enumerate(g2_result['state_times']):
        print(f"Estado {estado}: {tempo:.2f}")

if __name__ == "__main__":
    main()

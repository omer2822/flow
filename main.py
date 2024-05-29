import networkx as nx
import matplotlib.pyplot as plt
import csv


class Time:
    def __init__(self, day, skill, start=0, end=0, demand=0):
        self._day = day
        self._skill = skill
        self._start = start
        self._end = end
        self._demand = int(demand)
        self._time = f"{start}-{end}"

    @property
    def day(self):
        return self._day

    @property
    def numeric_day(self):
        days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        return days.index(self._day) + 1

    @property
    def skill(self):
        return self._skill

    @day.setter
    def day(self, value):
        self._day = value

    @skill.setter
    def skill(self, value):
        self._skill = value

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, value):
        self._start = value
        self._time = f"{self._start}-{self._end}"

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, value):
        self._end = value
        self._time = f"{self._start}-{self._end}"

    @property
    def demand(self):
        return self._demand

    @demand.setter
    def demand(self, value):
        self._demand = int(value)

    @property
    def time(self):
        return self._time

    def __repr__(self):
        return f"{self.numeric_day}:{self._start}-{self._end}:{self._demand}"
        return f"Time(day={self._day}, start={self._start}, end={self._end}, demand={self._demand})"

class Worker:
    def __init__(self, worker_id, name):
        self._id = worker_id
        self._name = name
        self._skills = []

    def add_skill(self, skill):
        if skill:
            self._skills.append(skill)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def skills(self):
        return self._skills

    def __repr__(self):
        return f"{self._name}"
        return f"Worker(id={self._id}, name={self._name}, skills={self._skills})"

def load_data_from_csv1(file_path):
    workers = {}
    skills = set()

    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            worker_id = row['Id']
            worker_name = row['Name']
            if worker_id not in workers:
                workers[worker_id] = Worker(worker_id, worker_name)

            worker = workers[worker_id]


            # Add non-empty skills
            if row['Skill1']:
                worker.add_skill(row['Skill1'])
                skills.add(row['Skill1'])
            if row['Skill2']:
                worker.add_skill(row['Skill2'])
                skills.add(row['Skill2'])
            if row['Skill3']:
                worker.add_skill(row['Skill3'])
                skills.add(row['Skill3'])


    return list(workers.values()), skills
#



def load_data_from_csv2(file_path):
    days = {}


    with open(file_path, 'r') as file:
        reader = csv.DictReader(file)

        for row in reader:
            day = row['Day']
            skill = row['Skill']
            start = row['Start']
            if (day,skill,start) not in days:
                days[(day,skill,start)] = Time(day,skill,start)
            time = days[((day,skill,start))]

            if row['End']:
                time.end = row['End']
            if row['Demand']:
                time.demand = row['Demand']


    return list(days.values())



def compute_max_flow(G, source, sink):
    flow_value, flow_dict = nx.maximum_flow(G, source, sink)
    return flow_value, flow_dict


def r():
    # Load data from CSV
    file_path1 = 'file1.csv'
    file_path2 = 'file3.csv'

    workers, skills = load_data_from_csv1(file_path1)

    demands = load_data_from_csv2(file_path2)

    max_hours=10

    G = build_network(workers, skills, demands, max_hours)

    # Compute the maximum flow
    flow_value, flow_dict = compute_max_flow(G, 'S', 'T')
    #print results
    assignments = []
    for worker in workers:
        for demand in demands:
            if demand in flow_dict[worker] and flow_dict[worker][demand] == 1:
                assignments.append((worker,demand))
                print(f'{worker} is assigned to {demand}')

    #prepare edge labels with flow/capacity
    edge_labels = {}
    for u,v,data in G.edges(data=True):
        flow = flow_dict[u][v] if v in flow_dict[u] else 0
        capacity = data['capacity']
        edge_labels[(u,v)] = f'{flow}/{capacity}'


    for layer, nodes in enumerate(nx.topological_generations(G)):
        # 'multipartite_layout' expects the layer as a node attribute, so add the
        # numerical layer value as a node attribute
        for node in nodes:
            G.nodes[node]["layer"] = layer

    pos = nx.multipartite_layout(G, subset_key="layer", scale=10)
    fig, ax = plt.subplots(figsize=(12,8))

    nx.draw_networkx(G, pos=pos, ax=ax, with_labels=True, node_size=1000, node_color='lightblue')

    # draw edge labels
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,font_size=10)

    #Highlight the assigments in red
    for worker, shift in assignments:
        nx.draw_networkx_edges(G, pos, edgelist=[(worker,shift)], edge_color='r',width=2,arrowstyle='-|>', arrowsize=20)

    ax.set_title("DAG layout in topological order")
    plt.axis('off')
    fig.tight_layout()
    plt.show()



def build_network(workers, skills, demands, max_hours):
    G = nx.DiGraph()

    source = 'S'
    sink = 'T'

    # Add source and sink nodes
    G.add_node(source)
    G.add_node(sink)

    # Add edges from source to worker availability nodes with capacity equal to max_hours
    for worker in workers:
        G.add_edge(source, worker, capacity=max_hours)

    for worker in workers:
        for demand in demands:
            if is_worker_has_skill(worker, demand.skill):
                G.add_edge(worker, demand, capacity=1)
    for demand in demands:
        G.add_edge(demand,sink, capacity=demand.demand)

    return G

def is_worker_has_skill(worker, skill):
    if skill in worker.skills:
        return True
    else:
        return False



if __name__ == '__main__':
    r()
    #
    # G = nx.complete_graph(5)
    # nx.draw(G)
    # plt.show()
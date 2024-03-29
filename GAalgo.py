import random as rd
import copy
from matplotlib import pyplot as plt


class Location:
    def __init__(self, name, x, y):
        self.name = name
        self.loc = (x, y)

    def distance_between(self, location2):
        assert isinstance(location2, Location)
        return ((self.loc[0] - location2.loc[0]) ** 2 + (self.loc[1] - location2.loc[1]) ** 2) ** (1 / 2)


def create_locations():
    locations = []
    xs = [82, 5, 12, 35, 95, 40, 84, 7, 43, 40, 60, 74]
    ys = [31, 2, 18, 25, 89, 72, 7, 29, 45, 65, 69, 47]
    cities = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    for x, y, name in zip(xs, ys, cities):
        locations.append(Location(name, x, y))
    return locations, xs, ys, cities


class Route:
    def __init__(self, path):
        # path is a list of Location obj
        self.path = path
        self.length = self._set_length()

    def _set_length(self):
        total_length = 0
        path_copy = self.path[:]
        from_here = path_copy.pop(0)
        init_node = copy.deepcopy(from_here)
        while path_copy:
            to_there = path_copy.pop(0)
            total_length += to_there.distance_between(from_here)
            from_here = copy.deepcopy(to_there)
        total_length += from_here.distance_between(init_node)
        return total_length


class GeneticAlgo:
    def __init__(self, locs, level, populations, variant, mutate_percent, elite_save_percent):
        self.locs = locs
        self.level = level
        self.variant = variant
        self.populations = populations
        self.mutates = int(populations * mutate_percent)
        self.elite = int(populations * elite_save_percent)

    def _find_path(self):
        # locs is a list containing all the Location obj
        locs_copy = self.locs[:]
        path = []
        while locs_copy:
            to_there = locs_copy.pop(locs_copy.index(rd.choice(locs_copy)))
            path.append(to_there)
        return path

    def _init_routes(self):
        routes = []
        for _ in range(self.populations):
            path = self._find_path()
            routes.append(Route(path))
        return routes

    def _get_next_route(self, routes):
        routes.sort(key=lambda x: x.length, reverse=False)
        elites = routes[:self.elite][:]
        crossovers = self._crossover(elites)
        return crossovers[:] + elites

    def _crossover(self, elites):
        # Route is a class type
        normal_breeds = []
        mutate_ones = []
        for _ in range(self.populations - self.mutates):
            father, mother = rd.choices(elites[:4], k=2)
            index_start = rd.randrange(0, len(father.path) - self.variant - 1)
            # list of Location obj
            father_gene = father.path[index_start: index_start + self.variant]
            father_gene_names = [loc.name for loc in father_gene]
            mother_gene = [gene for gene in mother.path if gene.name not in father_gene_names]
            mother_gene_cut = rd.randrange(1, len(mother_gene))
            # create new route path
            next_route_path = mother_gene[:mother_gene_cut] + father_gene + mother_gene[mother_gene_cut:]
            next_route = Route(next_route_path)
            # add Route obj to normal_breeds
            normal_breeds.append(next_route)

            # for mutate purpose
            copy_father = copy.deepcopy(father)
            idx = range(len(copy_father.path))
            gene1, gene2 = rd.sample(idx, 2)
            copy_father.path[gene1], copy_father.path[gene2] = copy_father.path[gene2], copy_father.path[gene1]
            mutate_ones.append(copy_father)
        mutate_breeds = rd.choices(mutate_ones, k=self.mutates)
        return normal_breeds + mutate_breeds

    def evolution(self):
        routes = self._init_routes()
        for _ in range(self.level):
            routes = self._get_next_route(routes)
        routes.sort(key=lambda x: x.length)
        return routes[0].path, routes[0].length


if __name__ == '__main__':
    my_locs, xs, ys, cities = create_locations()
    my_algo = GeneticAlgo(my_locs, level=50, populations=100, variant=3, mutate_percent=0.02, elite_save_percent=0.1)
    best_route, best_route_length = my_algo.evolution()
    best_route.append(best_route[0])
    print("最佳路線：", [loc.name for loc in best_route], "\n路徑長：", best_route_length)

    fig, ax = plt.subplots()
    ax.plot([loc.loc[0] for loc in best_route], [loc.loc[1] for loc in best_route], 'red', linestyle='-', marker='')
    ax.scatter(xs, ys)
    for i, txt in enumerate(cities):
        ax.annotate(txt, (xs[i], ys[i]))
    plt.show()
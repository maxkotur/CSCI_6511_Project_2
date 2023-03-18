import json
import time
import itertools

def read_file(file_name):
    landscape = []
    targets = dict()
    with open(file_name, 'r') as f:
        for line in f:
            if line[0] == "#":
                continue
            if line[0] == '\n':
                break
            row = []
            for i, x in enumerate(line):
                if i % 2 == 1:
                    continue
                if x == " ":
                    row.append(x)
                elif x == '\n':
                    break
                else:
                    row.append(x)
            landscape.append(row)
        size = len(landscape)
        for row in landscape:
            while len(row) != size:
                row.append(' ')

        f.readline()
        str_tile = f.readline()
        li = str_tile.split(", ")
        tiles = [''.join(i for i in word if i.isdigit()) for word in li]

        f.readline()
        f.readline()
        for line in f:
            if line == '\n':
                break

            words = line.split(":")

            targets[words[0]] = int(words[1])
    return landscape, tiles, targets

class Tile_Location:
    def __init__(self, index):
        self.index = index
        self.el = None
        self.outer = None
        self.full = {'ones': 0, 'twos': 0, 'threes': 0, 'fours': 0}

    def set_el_response(self, ones, twos, threes, fours):
        self.el = {'ones': ones, 'twos': twos, 'threes': threes, 'fours': fours}

    def set_outer_response(self, ones, twos, threes, fours):
        self.outer = {'ones': ones, 'twos': twos, 'threes': threes, 'fours': fours}

csp_complete = False


def get_csp_complete():
    global csp_complete
    return csp_complete


def set_csp_complete(val):
    global csp_complete
    csp_complete = val

def get_lcv_order(combos):
    print("Sorting MRV combos into Least Constrained Value (LCV) order...")
    combos.sort(key=lambda k: k[2], reverse=True)

def get_mvr(el_combo_counts, outer_combo_counts):
    mrv = None
    if el_combo_counts > outer_combo_counts:
        mrv = ['OUTER_BOUNDARY', 'EL_SHAPE']
    else:
        mrv = ['EL_SHAPE', 'OUTER_BOUNDARY']

    return mrv

def constraint_satisfied(actuals, targets):
    if actuals[0] == targets[0] and actuals[1] == targets[1] \
            and actuals[2] == targets[2] and actuals[3] == targets[3]:
        return True
    else:
        return False


def constraint_not_violated(actuals, targets):
    if actuals[0] <= targets[0] and actuals[1] <= targets[1] \
            and actuals[2] <= targets[2] and actuals[3] <= targets[3]:
        return True
    else:
        return False

def format_output(result, grid_width, tile_count):
    output_variable_value_maps = []

    for i in range(tile_count):
        if i in result[0]:
            output_variable_value_maps.append({
                'variable': i,
                'value': '1'
            })
        elif i in result[1]:
            output_variable_value_maps.append({
                'variable': i,
                'value': '2'
            })
        else:
            output_variable_value_maps.append({
                'variable': i,
                'value': '3'
            })

    output_variable_value_maps.sort(key=lambda k: k['variable'])

    tile_width = 4
    grid_output = chunks(output_variable_value_maps, int(grid_width / tile_width))

    i = 0
    result = []
    for column_index in range(int(grid_width / tile_width)):
        for row in grid_output:
            if row[column_index]['value'] == '1':
                result.append(str(i) + ' 4 OUTER_BOUNDARY')
            elif row[column_index]['value'] == '2':
                result.append(str(i) + ' 4 EL_SHAPE')
            elif row[column_index]['value'] == '3':
                result.append(str(i) + ' 4 FULL_BLOCK')
            i += 1
    return result


def chunks(original_list, size):
    chunked_list = []
    for i in range(0, len(original_list), size):
        chunked_list.append(original_list[i:i + size])

    return chunked_list

def apply_forward_check(combos, tile_locations, reserved_tile_locations, targets, type, last_var):
    valid_combos = []
    for combo in combos:
        overlap = False
        for element in combo:
            if element in reserved_tile_locations:
                overlap = True
                break

        if not overlap:
            actuals = forward_check(combo, tile_locations, targets, type, last_var)
            if get_csp_complete():
                return combo
            elif actuals != -1:
                min_delta = min([targets[0] - actuals[0], targets[1] - actuals[1], targets[2] - actuals[2],
                                 targets[3] - actuals[3]])
                valid_combos.append([combo, actuals, min_delta])

    return valid_combos


def forward_check(combo, tile_locations, targets, type, last_var):
    actuals = [0, 0, 0, 0]
    for location in combo:
        if type == 'EL_SHAPE':
            actuals[0] += tile_locations[location].el['ones']
            actuals[1] += tile_locations[location].el['twos']
            actuals[2] += tile_locations[location].el['threes']
            actuals[3] += tile_locations[location].el['fours']
        else:
            actuals[0] += tile_locations[location].outer['ones']
            actuals[1] += tile_locations[location].outer['twos']
            actuals[2] += tile_locations[location].outer['threes']
            actuals[3] += tile_locations[location].outer['fours']

    if last_var and constraint_satisfied(actuals, targets):
        set_csp_complete(True)
        return actuals
    elif constraint_not_violated(actuals, targets):
        return actuals
    else:
        return -1

def filter_domains(tile_counts, tile_locations, targets):
    targets = [targets['1'], targets['2'], targets['3'], targets['4']]
    location_count = len(tile_locations)

    el_combo_counts = get_combo_count(location_count, tile_counts, 'EL_SHAPE')
    outer_combo_counts = get_combo_count(location_count, tile_counts, 'OUTER_BOUNDARY')

    combos = {'EL_SHAPE': itertools.combinations(range(location_count), tile_counts['EL_SHAPE']),
              'OUTER_BOUNDARY': itertools.combinations(range(location_count), tile_counts['OUTER_BOUNDARY'])}

    mrv = get_mvr(el_combo_counts, outer_combo_counts)
    print("Minimum Remaining Values (MRV): " + mrv[0])

    print("Applying Forward Checking on MRV combos...")
    valid_mrv = apply_forward_check(combos[mrv[0]], tile_locations, [], targets, mrv[0], False)
    print(f"Total Combos MRV after Forward Check: {len(valid_mrv):,}")

    get_lcv_order(valid_mrv)

    return enforce_consistency(combos, targets, valid_mrv, mrv, tile_locations)


def enforce_consistency(combos, targets, valid_mrv, mrv, tile_locations):
    print("Applying Arc Consistency to remaining combos...")
    mrv_2_combos = list(combos[mrv[1]])
    for valid_lcv_combos in valid_mrv:
        updated_targets = [targets[0] - valid_lcv_combos[1][0], targets[1] - valid_lcv_combos[1][1],
                           targets[2] - valid_lcv_combos[1][2], targets[3] - valid_lcv_combos[1][3]]
        valid_full_combos = apply_forward_check(mrv_2_combos, tile_locations, valid_lcv_combos[0], updated_targets,
                                                mrv[1], True)
        if get_csp_complete():
            print("Solution found!")

            # Order Matters for Print function
            if mrv[0] == 'EL_SHAPE':
                return [valid_full_combos, valid_lcv_combos[0]]
            else:
                return [valid_lcv_combos[0], valid_full_combos]


def get_combo_count(location_count, tile_counts, type):
    combos = itertools.combinations(range(location_count), tile_counts[type])
    combo_counts = sum(1 for ignore in combos)
    print(f"Total Combos {type}: {combo_counts:,}")
    return combo_counts

def get_landscape(file):
    landscape = []
    longest_row_length = 0
    reading_landscape = False
    with open(file) as f:
        for i in f.readlines():
            if i.startswith('# Landscape'):  # Next line starts landscape
                reading_landscape = True
                continue

            if reading_landscape:
                if i in ['\n', '\r\n']:  # Blank line represents end of landscape
                    # Handle cases where last values are spaces
                    for row in landscape:
                        while len(row) < longest_row_length:
                            row.append(' ')
                    return landscape
                else:
                    row = list(i[::2])
                    if len(row) > longest_row_length:
                        longest_row_length = len(row)
                    landscape.append(row)



def get_tile_counts(file):
    reading_tiles = False
    with open(file) as f:
        for i in f.readlines():
            if i.startswith('# Tiles:'):  # Next line starts tile counts
                reading_tiles = True
                continue

            # Transform input to valid json
            if reading_tiles:
                i = i.replace('=', ':')
                i = i.replace('OUTER_BOUNDARY', '"OUTER_BOUNDARY"')
                i = i.replace('EL_SHAPE', '"EL_SHAPE"')
                i = i.replace('FULL_BLOCK', '"FULL_BLOCK"')
                i = i.replace('\n', '')
                return json.loads(i)


# def get_targets(file):
#     targets = {}
#     reading_targets = False
#     with open(file) as f:
#         for i in f.readlines():
#             if i.startswith('# Targets:'):  # Next line starts tile counts
#                 reading_targets = True
#                 continue
#
#             # Transform input to valid json
#             if reading_targets:
#                 if i in ['\n', '\r\n']:  # Blank line represents end of targets
#                     return targets
#                 else:
#                     targets[i[0]] = int(i.rstrip()[2:])
#
#         return targets  # Handle case where the line after targets is EOF

def validate_landscape(landscape):
    # Check list length is a multiple of 4
    if len(landscape) % 4 != 0:
        raise ValueError('The landscape is not a multiple of 4!')

    # Check lines length is a multiple of 4
    for i in landscape:
        if len(i) % 4 != 0:
            raise ValueError('The landscape is not a multiple of 4!')


# Start at coordinate 0, 0 (top left) and work left to right, line by line, top to bottom
def create_tiles(landscape):
    tile_locations = []

    tile_size = 4
    landscape_tile_width = int(len(landscape[0])/tile_size)
    landscape_tile_length = int(len(landscape)/tile_size)
    outer_visible_coordinates = [[1, 1], [1, 2], [2, 1], [2, 2]]
    el_visible_coordinates = [[1, 1], [1, 2], [1, 3], [2, 1], [2, 2], [2, 3], [3, 1], [3, 2], [3, 3]]

    tile_index = 0
    for y in range(landscape_tile_length):
        for x in range(landscape_tile_width):
            tile_location = Tile_Location(tile_index)
            el = {'ones': 0, 'twos': 0, 'threes': 0, 'fours': 0}
            outer = {'ones': 0, 'twos': 0, 'threes': 0, 'fours': 0}

            x_offset = x * tile_size
            y_offset = y * tile_size

            for coordinate in outer_visible_coordinates:
                value_at_coordinate = landscape[y_offset + coordinate[0]][x_offset + coordinate[1]]
                if value_at_coordinate == '1':
                    outer['ones'] += 1
                elif value_at_coordinate == '2':
                    outer['twos'] += 1
                elif value_at_coordinate == '3':
                    outer['threes'] += 1
                elif value_at_coordinate == '4':
                    outer['fours'] += 1

            for coordinate in el_visible_coordinates:
                value_at_coordinate = landscape[y_offset + coordinate[0]][x_offset + coordinate[1]]
                if value_at_coordinate == '1':
                    el['ones'] += 1
                elif value_at_coordinate == '2':
                    el['twos'] += 1
                elif value_at_coordinate == '3':
                    el['threes'] += 1
                elif value_at_coordinate == '4':
                    el['fours'] += 1

            tile_location.set_el_response(el['ones'], el['twos'], el['threes'], el['fours'])
            tile_location.set_outer_response(outer['ones'], outer['twos'], outer['threes'], outer['fours'])
            tile_locations.append(tile_location)
            tile_index += 1

    return tile_locations

# def main(file):
if __name__ == '__main__':
    file = 'testcases/testcase3.txt'
    print("Processing: " + file)

    # file = 'testcases/testcase10.txt'
    # landscape = get_landscape(file)
    landscape, tiles, targets = read_file(file)
    tiles = {'EL_SHAPE': int(tiles[0]), 'OUTER_BOUNDARY': int(tiles[1]), 'FULL_BLOCK': int(tiles[2])}
    for i in landscape:
        print(i)
    validate_landscape(landscape)

    # Tile counts represents the input or the number of tiles we have available
    # tiles = get_tile_counts(file)
    # Tile_Locations represents the 4x4 locations that a tile can occupy
    # A Tile_Location holds the bush counts that would be visible if overlaid by each tile type
    tile_locations = create_tiles(landscape)
    # print(targets)
    # targets = get_targets(file)

    start = time.time()
    print(tiles)
    print(f"Number of Tiles: {len(tile_locations)}")
    print(targets)
    result = filter_domains(tiles, tile_locations, targets)

    end = time.time()

    print("Time: " + str(end - start) + "s")
    result = format_output(result, int(len(landscape[0]) / 4), len(tile_locations))
    print('\n'.join(result))
    # return result


#     file = sys.argv[1]
#     main(file)

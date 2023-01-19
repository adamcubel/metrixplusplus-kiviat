import numpy as np
import matplotlib.pyplot as plt

from metrixpp.mpp import api
from metrixpp.mpp import utils

import os

DIGIT_COUNT = 2
KIVIAT_IMAGE_NAME = 'kiviat.png'

def get_all_data(loader, paths):
    exit_code = 0
    for (ind, path) in enumerate(paths):
        path = utils.preprocess_path(path)
        
        aggregated_data = loader.load_aggregated_data(path)
        
        aggregated_data_tree = {}
        subdirs = []
        subfiles = []
        if aggregated_data != None:
            aggregated_data_tree = aggregated_data.get_data_tree()
            subdirs = sorted(aggregated_data.get_subdirs())
            subfiles = sorted(aggregated_data.get_subfiles())
        else:
            utils.report_bad_path(path)
            exit_code += 1
        
        file_data = loader.load_file_data(path)
        file_data_tree = {}
        if file_data != None:
            file_data_tree = file_data.get_data_tree()
            append_regions(file_data_tree, file_data)
        
        data = {"info": {"path": path, "id": ind + 1},
                "aggregated-data": aggregated_data_tree,
                "file-data": file_data_tree,
                "subdirs": subdirs,
                "subfiles": subfiles}

        return data, exit_code

def append_regions(file_data_tree, file_data):
    regions = []
    for region in file_data.iterate_regions():
        region_data_tree = region.get_data_tree()
        is_modified = None
        regions.append({"info": {"name" : region.name,
                                'type': api.Region.T().to_str(region.get_type()),
                                'modified': is_modified,
                                'cursor' : region.cursor,
                                'line_begin': region.line_begin,
                                'line_end': region.line_end,
                                'offset_begin': region.begin,
                                'offset_end': region.end},
                                "data": region_data_tree})
    file_data_tree['regions'] = regions

def get_value_from_data(data, namespace, field, attr):
    retval = None
    
    if namespace in list(data['aggregated-data'].keys()):
        if field in list(data['aggregated-data'][namespace].keys()):
            if attr in list(data['aggregated-data'][namespace][field].keys()):
                if isinstance(data['aggregated-data'][namespace][field][attr], float):
                    # round the data to reach same results on platforms with different precision
                    retval = round(data['aggregated-data'][namespace][field][attr], DIGIT_COUNT)
                else:
                    retval = data['aggregated-data'][namespace][field][attr]
            else:
                print("Could not find attribute in data - Namespace: " + namespace + " Field: " + field + " Attribute: " + attr)
        else:
            print("Could not find attribute in data - Namespace: " + namespace + " Field: " + field)
    else:
        print("Could not find namespace in data - Namespace: " + namespace)

    return retval

def get_plottable_data_for_percent_comments(data):
    retval = 0
    total_lines = get_value_from_data(data, "std.code.lines", "total", "total")
    comment_lines = get_value_from_data(data, "std.code.lines", "comments", "total")

    if total_lines is None:
        print("Could not retrieve total lines from data")
    if comment_lines is None:
        print("Could not retrieve comment lines from data")

    if total_lines is not None and comment_lines is not None:
        retval = (comment_lines / total_lines) * 100
    return retval

def get_plottable_data_for_methods_per_class(data):
    retval = 0
    methods_per_class = get_value_from_data(data, "std.code.member", "methods", "avg")

    if methods_per_class is None:
        print("Could not retrieve average methods per class from data")
    else:
        retval = methods_per_class
    return retval

def get_plottable_data_for_avg_complexity(data):
    retval = 0
    avg_complexity = get_value_from_data(data, "std.code.complexity", "cyclomatic", "avg")

    if avg_complexity is None:
        print("Could not retrieve average methods per class from data")
    else:
        retval = avg_complexity + 1 # This is because the tool starts from zero instead of one.
    return retval

def get_plottable_data_for_max_complexity(data):
    retval = 0
    max_complexity = get_value_from_data(data, "std.code.complexity", "cyclomatic", "max")

    if max_complexity is None:
        print("Could not retrieve average methods per class from data")
    else:
        retval = max_complexity
    return retval

def get_plottable_data_for_avg_depth(data):
    retval = 0
    avg_depth = get_value_from_data(data, "std.code.complexity", "maxindent", "avg")

    if avg_depth is None:
        print("Could not retrieve average methods per class from data")
    else:
        retval = avg_depth
    return retval

def get_plottable_data_for_max_depth(data):
    retval = 0
    max_depth = get_value_from_data(data, "std.code.complexity", "maxindent", "max")

    if max_depth is None:
        print("Could not retrieve average methods per class from data")
    else:
        retval = max_depth
    return retval

class Plugin(api.Plugin, api.IConfigurable, api.IRunable):
    def create_graph(self, rect=None):
        if rect is None:
            rect = [0.15, 0.15, 0.65, 0.65]

        self.figure = plt.figure(figsize=(10, 9))

        self.axes_titles = [
            '% Comments [15-25]', 
            'Avg Complexity [2.0-4.5]',
            'Avg Depth [1.0-2.5]', 
            'Max Depth [3-6]', 
            'Max Complexity [2-8]', 
            'Avg Statements/Method [5-10]',
            'Methods/Class [4-20]'
            ]

        self.acceptable_min = [
            15,
            2.0,
            1.0,
            3,
            2,
            5,
            4
        ]

        self.acceptable_max = [
            25,
            4.5,
            2.5,
            6,
            8,
            10,
            20
        ]

        # Self imposed limits for each axis of graph
        self.limits = [
            50,
            9,
            5,
            12,
            16,
            20,
            40
        ]

        self.scale_limit = 300
        self.scale_lower_bound = 100
        self.scale_upper_bound = 200

        self.n_ticks = 5

        self.n = len(self.axes_titles)

        self.angles = [a if a <= 360. else a - 360. for a in np.arange(90, 90 + 360, 360.0 / self.n)]
        self.axes = [self.figure.add_axes(rect, projection='polar', label=i) for i in self.axes_titles]

        # Setup primary axis
        self.ax = self.axes[0]
        self.ax.set_thetagrids(self.angles, labels=self.axes_titles, fontsize=12, color="black")
        self.ax.tick_params(direction='out', pad=30, grid_linewidth=1.5, grid_color='#0d7f7f')
        self.ax.fill_between(np.linspace(np.deg2rad(self.angles[0]), np.deg2rad(self.angles[0] + 360), 100), self.scale_lower_bound, self.scale_upper_bound, color='#acfc8c', edgecolor='#0d7f7f')
        self.ax.set_title("Kiviat Metrics Graph", va='bottom')
        self.ax.set_ylim(0, self.scale_limit) # limit

        for ax in self.axes[1:]:
            ax.patch.set_visible(False)
            ax.grid(False)
            ax.xaxis.set_visible(False)
            self.ax.yaxis.grid(False)

        for ax, angle, limit in zip(self.axes, self.angles, self.limits):
            ticks = [(limit/self.n_ticks)*i for i in range(self.n_ticks+1)]
            ax.set_rgrids(ticks, angle=angle, label=ticks)
            ax.spines['polar'].set_visible(False)
            ax.set_yticklabels([]) # hide the tick labels
        
    def plot(self, values, *args, **kw):
        limits = np.array(self.limits)

        plot_values = []
        for value, acceptable_min, acceptable_max, limit in zip(np.array(values), self.acceptable_min, self.acceptable_max, limits):
            plot_value = None
            if value <= acceptable_min:
                plot_value = value / acceptable_min * 100
            elif value > acceptable_min and value <= acceptable_max:
                plot_value = ((value - acceptable_min) / (acceptable_max - acceptable_min) * 100) + self.scale_lower_bound
            elif value > acceptable_max and value <= limit:
                plot_value = ((value - acceptable_max) / (limit - acceptable_max) * 100) + self.scale_upper_bound
            else:
                plot_value = self.scale_limit
            plot_values.append(plot_value)

        angles = np.deg2rad(np.r_[self.angles, self.angles[0]])
        plot_values = np.array(plot_values)
        plot_values = np.r_[plot_values, plot_values[0]]

        self.ax.plot(angles, plot_values, *args, **kw)
        for angle, value, og_value in zip(angles, plot_values, values):
            self.ax.annotate(
                str(round(og_value, 2)),
                xy=[angle, value],
                xytext=(6, 7),
                textcoords='offset points',
                clip_on=False,
                weight='bold')

    def declare_configuration(self, parser):
        self.parser = parser
        parser.add_option("--graph-dir", "--gd", default='',
                          help="Location for where to save the Kiviat Graph. "
                          "[default: directory of the kiviat plugin]")
    
    def configure(self, options):
        self.save_dir = options.__dict__['graph_dir']

        if self.save_dir != "":
            if not os.path.exists(self.save_dir):
                self.parser.error("Option --graph-dir requires a path that exists to save the resulting image of the Kiviat chart.")

    def initialize(self):
        self.create_graph()

    def save(self, file_path):
        self.figure.savefig(file_path)

    def run(self, args):
        loader = self.get_plugin('metrixpp.mpp.dbf').get_loader()

        paths = None
        if len(args) == 0:
            paths = [""]
        else:
            paths = args

        (data, exit_code) = get_all_data(loader, paths)

        if exit_code == 0:
            percent_comments = get_plottable_data_for_percent_comments(data)
            avg_complexity = get_plottable_data_for_avg_complexity(data)
            avg_depth = get_plottable_data_for_avg_depth(data)
            max_depth = get_plottable_data_for_max_depth(data)
            max_complexity = get_plottable_data_for_max_complexity(data)
            # TODO: Get 'Avg Statements/Method [5-10]' - not currently possible with current metrics gathering options
            methods_per_class = get_plottable_data_for_methods_per_class(data)
            plotting_list = [percent_comments, avg_complexity, avg_depth, max_depth, max_complexity, 0, methods_per_class]

            self.plot(
                plotting_list, 
                lw=1, 
                color='r', 
                alpha=0.9, 
                marker="P", 
                markeredgecolor='k', 
                markersize=12, 
                label='first', 
                clip_on=False)
            self.save(os.path.join(self.save_dir, KIVIAT_IMAGE_NAME))
        else:
            print("Error getting the data from the database.")

        return exit_code
import numpy as np
import json
import matplotlib.pyplot as plt
import os.path


def read_all_data(files):
    dict_dynamic = {}
    for name, file in files.items():
        with open("../" + file, 'r') as outfile:
            dict_dynamic[name] = {}
            print("Reading " + file)
            data = json.load(outfile)
            for key, value in data.items():
                dict_dynamic[name][key] = value
                dict_dynamic[name][key]["Times"] = np.asarray(dict_dynamic[name][key]["Times"])
                dict_dynamic[name][key]["Values"] = np.asarray(dict_dynamic[name][key]["Values"])
                dict_dynamic[name][key]["Domains"] = np.asarray(dict_dynamic[name][key]["Domains"])
            del (data)
    return dict_dynamic


def setAxLinesBW(ax):
    """
    Take each Line2D in the axes, ax, and convert the line style to be
    suitable for black and white viewing.
    """
    MARKERSIZE = 3

    COLORMAP = {
        'b': {'marker': None, 'dash': (None, None)},
        'g': {'marker': None, 'dash': [5, 5]},
        'r': {'marker': None, 'dash': [5, 3, 1, 3]},
        'c': {'marker': None, 'dash': [1, 3]},
        'm': {'marker': None, 'dash': [5, 2, 5, 2, 5, 10]},
        'y': {'marker': None, 'dash': [5, 3, 1, 2, 1, 10]},
        'k': {'marker': 'o', 'dash': (None, None)}  # [1,2,1,10]}
    }

    lines_to_adjust = ax.get_lines()
    try:
        lines_to_adjust += ax.get_legend().get_lines()
    except AttributeError:
        pass

    for line in lines_to_adjust:
        origColor = line.get_color()
        line.set_color('black')
        line.set_dashes(COLORMAP[origColor]['dash'])
        line.set_marker(COLORMAP[origColor]['marker'])
        line.set_markersize(MARKERSIZE)


def setFigLinesBW(fig):
    """
    Take each axes in the figure, and for each line in the axes, make the
    line viewable in black and white.
    """
    for ax in fig.get_axes():
        setAxLinesBW(ax)


def prepare_data_0(dict_dynamic, case1, case2, tlim=2*365):

    t1 = dict_dynamic[case1]['node_A.w']['Times']
    t2 = dict_dynamic[case2]['node_A.w']['Times']

    plot_dict = [
        {
            'variable': 'condenser.Rf',
            'y_label': 'Fouling resistance at z=1 outlet (10$^{-3}$ m$^2$K/W)', 'leg_position': 'best', 'ylim': None,
            't1': t1[t1 <= tlim],
            't2': t2[t2 <= tlim],
            'x1': dict_dynamic[case1]['condenser.Rf']['Values'][:, -1, 0][t1 <= tlim] * 1e3,
            'x2': dict_dynamic[case2]['condenser.Rf']['Values'][:, -1, 0][t2 <= tlim] * 1e3,
            'color': "black",
        },

        {
         'variable': 'node_A.w',
         'y_label': 'Cooling water flowrate (kg/s)', 'leg_position': 'best',
         't1': t1[t1 <= tlim],
         't2': t2[t2 <= tlim],
         'x1': dict_dynamic[case1]['node_A.w']['Values'][t1 <= tlim],
         'x2': dict_dynamic[case2]['node_A.w']['Values'][t2 <= tlim],
         'color': 'green',
         },

        {
         'variable': 'condenser.Text',
         'y_label': 'Steam temperature (K)', 'leg_position': 'best',
         't1': t1[t1 <= tlim],
         't2': t2[t2 <= tlim],
         'x1': dict_dynamic[case1]['condenser.Text']['Values'][t1 <= tlim],
         'x2': dict_dynamic[case2]['condenser.Text']['Values'][t2 <= tlim],
         'color': 'red',
         },

        {
         'variable': 'condenser.Pext',
         'y_label': 'Steam pressure (Pa)', 'leg_position': 'best',
         't1': t1[t1 <= tlim],
         't2': t2[t2 <= tlim],
         'x1': dict_dynamic[case1]['condenser.Pext']['Values'][t1 <= tlim],
         'x2': dict_dynamic[case2]['condenser.Pext']['Values'][t2 <= tlim],
         'color': 'black',
         },

        {
         'variable': 'condenser.kcond',
         'y_label': 'Condensate flowrate (kg/s)', 'leg_position': 'best',
         't1': t1[t1 <= tlim],
         't2': t2[t2 <= tlim],
         'x1': dict_dynamic[case1]['condenser.kcond']['Values'][t1 <= tlim],
         'x2': dict_dynamic[case2]['condenser.kcond']['Values'][t2 <= tlim],
         'color': 'green',
         },

        {
         'variable': 'condenser.Qtotal',
         'y_label': 'Heat Load (MW)', 'leg_position': 'best',
         't1': t1[t1 <= tlim],
         't2': t2[t2 <= tlim],
         'x1': np.sum(dict_dynamic[case1]['condenser.Qtotal']['Values'] / 1e6, axis=1)[t1 <= tlim],
         'x2': np.sum(dict_dynamic[case2]['condenser.Qtotal']['Values'] / 1e6, axis=1)[t2 <= tlim],
         'color': 'darkmagenta',

         },

        {
         'variable': 'node_A.P',
         'y_label': 'Node 1 pressure (Pa)', 'leg_position': 'best',
         't1': t1[t1 <= tlim],
         't2': t2[t2 <= tlim],
         'x1': dict_dynamic[case1]['node_A.P']['Values'][t1 <= tlim],
         'x2': dict_dynamic[case2]['node_A.P']['Values'][t2 <= tlim],
         'color': 'green',
         },
    ]

    return plot_dict


def plot_curves_0(plot_dict, with_legend=True, scenario='-'):
    i = 0
    for plot_dict_i in plot_dict:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(plot_dict_i['t1'], plot_dict_i['x1'], 'k-', lw=2.5, label="With fouling")
        ax.plot(plot_dict_i['t2'], plot_dict_i['x2'], 'k--', lw=2.5, label="Without fouling")
        ax.set_xlabel('Time (days)')
        ax.set_ylabel(plot_dict_i['y_label'])
        for ax in plt.gcf().axes:
            for line in ax.get_lines():
                line.set_color(plot_dict_i['color'])
        ax.autoscale(enable=True, axis='both', tight=None)

        if with_legend:
            plt.legend(frameon=False, loc=plot_dict_i['leg_position'], ncol=1, handlelength=4, numpoints=1)

        plt.savefig(os.path.join('./pdfs/', '{}_curve0_{}.pdf'.format(scenario, plot_dict_i["variable"])), dpi=300)

        plt.show()
        i += 1


def prepare_data_1(dict_dynamic, case1, case2, tlim=2*365):

    t1 = dict_dynamic[case1]['condenser.Rf']['Times']
    t2 = dict_dynamic[case2]['condenser.Rf']['Times']

    plot_dict = [
        {
         'variable': 'condenser.Rfinlet',
         'y_label': 'Mean fouling resistance (10$^{-3}$ m$^2$K/W)', 'leg_position': 'best', 'ylim': None,
         't1': t1[t1 <= tlim],
         't2': t2[t2 <= tlim],
         'x1': np.mean(dict_dynamic[case1]['condenser.Rf']['Values'][:, 0, :], axis=1)[t1 <= tlim] * 1e3,
         'x2': np.mean(dict_dynamic[case2]['condenser.Rf']['Values'][:, 0, :], axis=1)[t2 <= tlim] * 1e3,
         'title': "Inlet",
         'color': "black",
         'edgecolor': "lightgray",
         },
        {
         'variable': 'condenser.Rf',
         'y_label': 'Fouling resistance (10$^{-3}$ m$^2$K/W)', 'leg_position': 'best', 'ylim': None,
         't1': t1[t1 <= tlim],
         't2': t2[t2 <= tlim],
         'x1': dict_dynamic[case1]['condenser.Rf']['Values'][:, -1, 0][t1 <= tlim] * 1e3,
         'x2': dict_dynamic[case2]['condenser.Rf']['Values'][:, -1, 0][t2 <= tlim] * 1e3,
         'title': "Outlet for z=1",
         'color': "black",
         'edgecolor': "lightgray",
         },
        {
         'variable': 'condenser.Rf',
         'y_label': 'Fouling resistance (10$^{-3}$ m$^2$K/W)', 'leg_position': 'best', 'ylim': None,
         't1': t1[t1 <= tlim],
         't2': t2[t2 <= tlim],
         'x1': dict_dynamic[case1]['condenser.Rf']['Values'][:, -1, -1][t1 <= tlim] * 1e3,
         'x2': dict_dynamic[case2]['condenser.Rf']['Values'][:, -1, -1][t2 <= tlim] * 1e3,
         'title': "Outlet for z=34",
         'color': "black",
         'edgecolor': "lightgray",
         },
        {
         'variable': 'condenser.Rfoutlet',
         'y_label': 'Mean fouling resistance (10$^{-3}$ m$^2$K/W)', 'leg_position': 'best', 'ylim': None,
         't1': t1[t1 <= tlim],
         't2': t2[t2 <= tlim],
         'x1': np.mean(dict_dynamic[case1]['condenser.Rf']['Values'][:, -1, :], axis=1)[t1 <= tlim] * 1e3,
         'x2': np.mean(dict_dynamic[case2]['condenser.Rf']['Values'][:, -1, :], axis=1)[t2 <= tlim] * 1e3,
         'title': "Outlet",
         'color': "black",
         'edgecolor': "lightgray",
         },

        {
         'variable': 'condenser.T',
         'y_label': 'Cooling water temperature (K)', 'leg_position': 'best', 'ylim': None,
         't1': t1[t1 <= tlim],
         't2': t2[t2 <= tlim],
         'x1': dict_dynamic[case1]['node_C.T']['Values'][t1 <= tlim],
         'x2': dict_dynamic[case2]['node_C.T']['Values'][t2 <= tlim],
         'title': "Outlet",
         'color': "red",
         'edgecolor': "bisque",
         },

        {
         'variable': 'condenser.Tinlet',
         'y_label': 'Mean water temperature (K)', 'leg_position': 'best', 'ylim': None,
         't1': t1[t1 <= tlim],
         't2': t2[t2 <= tlim],
         'x1': np.mean(dict_dynamic[case1]['condenser.T']['Values'][:, 0, :], axis=1)[t1 <= tlim],
         'x2': np.mean(dict_dynamic[case2]['condenser.T']['Values'][:, 0, :], axis=1)[t2 <= tlim],
         'title': "Inlet",
         'color': "red",
         'edgecolor': "bisque",
         },

        {
            'variable': 'condenser.Tinlet',
            'y_label': 'Water temperature (K)', 'leg_position': 'best', 'ylim': None,
            't1': t1[t1 <= tlim],
            't2': t2[t2 <= tlim],
            'x1': dict_dynamic[case1]['condenser.T']['Values'][:, 0, 0][t1 <= tlim],
            'x2': dict_dynamic[case2]['condenser.T']['Values'][:, 0, 0][t2 <= tlim],
            'title': "Inlet for z=1",
            'color': "red",
            'edgecolor': "bisque",
        },

        {
            'variable': 'condenser.Tinlet',
            'y_label': 'Water temperature (K)', 'leg_position': 'best', 'ylim': None,
            't1': t1[t1 <= tlim],
            't2': t2[t2 <= tlim],
            'x1': dict_dynamic[case1]['condenser.T']['Values'][:, 0, -1][t1 <= tlim],
            'x2': dict_dynamic[case2]['condenser.T']['Values'][:, 0, -1][t2 <= tlim],
            'title': "Inlet for z=34",
            'color': "red",
            'edgecolor': "bisque",
        },

        {
         'variable': 'condenser.Toutlet',
         'y_label': 'Mean water temperature (K)', 'leg_position': 'best', 'ylim': None,
         't1': t1[t1 <= tlim],
         't2': t2[t2 <= tlim],
         'x1': np.mean(dict_dynamic[case1]['condenser.T']['Values'][:, -1, :], axis=1)[t1 <= tlim],
         'x2': np.mean(dict_dynamic[case2]['condenser.T']['Values'][:, -1, :], axis=1)[t2 <= tlim],
         'title': "Outlet",
         'color': "red",
         'edgecolor': "bisque",
         },

        {
         'variable': 'condenser.Toutlet',
         'y_label': 'Water temperature (K)', 'leg_position': 'best', 'ylim': None,
         't1': t1[t1 <= tlim],
         't2': t2[t2 <= tlim],
         'x1': dict_dynamic[case1]['condenser.T']['Values'][:, -1, 0][t1 <= tlim],
         'x2': dict_dynamic[case2]['condenser.T']['Values'][:, -1, 0][t2 <= tlim],
         'title': "Outlet for z=1",
         'color': "red",
         'edgecolor': "bisque",
         },

        {
         'variable': 'condenser.Toutlet',
         'y_label': 'Water temperature (K)', 'leg_position': 'best', 'ylim': None,
         't1': t1[t1 <= tlim],
         't2': t2[t2 <= tlim],
         'x1': dict_dynamic[case1]['condenser.T']['Values'][:, -1, -1][t1 <= tlim],
         'x2': dict_dynamic[case2]['condenser.T']['Values'][:, -1, -1][t2 <= tlim],
         'title': "Outlet for z=34",
         'color': "red",
         'edgecolor': "bisque",
         },

        {
         'variable': 'condenser.vinlet',
         'y_label': 'Mean fluid velocity (m/s)', 'leg_position': 'best', 'ylim': None,
         't1': t1[t1 <= tlim],
         't2': t2[t2 <= tlim],
         'x1': np.mean(dict_dynamic[case1]['condenser.v']['Values'][:, 0, :], axis=1)[t1 <= tlim],
         'x2': np.mean(dict_dynamic[case2]['condenser.v']['Values'][:, 0, :], axis=1)[t2 <= tlim],
         'title': "Inlet",
         'color': "blue",
         'edgecolor': "skyblue",
         },

        {
            'variable': 'condenser.vinlet',
            'y_label': 'Fluid velocity (m/s)', 'leg_position': 'best', 'ylim': None,
            't1': t1[t1 <= tlim],
            't2': t2[t2 <= tlim],
            'x1': dict_dynamic[case1]['condenser.v']['Values'][:, 0, 0][t1 <= tlim],
            'x2': dict_dynamic[case2]['condenser.v']['Values'][:, 0, 0][t2 <= tlim],
            'title': "Inlet for z=1",
            'color': "blue",
            'edgecolor': "skyblue",
        },
        {
            'variable': 'condenser.vinlet',
            'y_label': 'Fluid velocity (m/s)', 'leg_position': 'best', 'ylim': None,
            't1': t1[t1 <= tlim],
            't2': t2[t2 <= tlim],
            'x1': dict_dynamic[case1]['condenser.v']['Values'][:, 0, -1][t1 <= tlim],
            'x2': dict_dynamic[case2]['condenser.v']['Values'][:, 0, -1][t2 <= tlim],
            'title': "Inlet for z=34",
            'color': "blue",
            'edgecolor': "skyblue",
        },

        {
         'variable': 'condenser.voutlet',
         'y_label': 'Mean fluid velocity (m/s)', 'leg_position': 'best', 'ylim': None,
         't1': t1[t1 <= tlim],
         't2': t2[t2 <= tlim],
         'x1': np.mean(dict_dynamic[case1]['condenser.v']['Values'][:, -1, :], axis=1)[t1 <= tlim],
         'x2': np.mean(dict_dynamic[case2]['condenser.v']['Values'][:, -1, :], axis=1)[t2 <= tlim],
         'title': "Outlet",
         'color': "blue",
         'edgecolor': "skyblue",
         },

        {
            'variable': 'condenser.voutlet',
            'y_label': 'Fluid velocity (m/s)', 'leg_position': 'best', 'ylim': None,
            't1': t1[t1 <= tlim],
            't2': t2[t2 <= tlim],
            'x1': dict_dynamic[case1]['condenser.v']['Values'][:, -1, 0][t1 <= tlim],
            'x2': dict_dynamic[case2]['condenser.v']['Values'][:, -1, 0][t2 <= tlim],
            'title': "Outlet for z=1",
            'color': "blue",
            'edgecolor': "skyblue",
        },
        {
            'variable': 'condenser.voutlet',
            'y_label': 'Fluid velocity (m/s)', 'leg_position': 'best', 'ylim': None,
            't1': t1[t1 <= tlim],
            't2': t2[t2 <= tlim],
            'x1': dict_dynamic[case1]['condenser.v']['Values'][:, -1, -1][t1 <= tlim],
            'x2': dict_dynamic[case2]['condenser.v']['Values'][:, -1, -1][t2 <= tlim],
            'title': "Outlet for z=34",
            'color': "blue",
            'edgecolor': "skyblue",
        },
    ]

    return plot_dict


def plot_curves_1(plot_dict, with_legend=True, scenario='short-term'):
    i = 0
    for plot_dict_i in plot_dict:
        fig = plt.figure()
        ax = fig.add_subplot(111)

        ax.plot(plot_dict_i['t1'], plot_dict_i['x1'], 'k-', lw=2.5, label="With fouling")
        ax.plot(plot_dict_i['t2'], plot_dict_i['x2'], 'k--', lw=2.5, label="Without fouling")
        for ax in plt.gcf().axes:
            for line in ax.get_lines():
                line.set_color(plot_dict_i['color'])

        ax.set_xlabel('Time (days)')
        ax.set_ylabel(plot_dict_i['y_label'])
        ax.autoscale(enable=True, axis='both', tight=None)

        if with_legend:
            plt.legend(frameon=False, loc=plot_dict_i['leg_position'], ncol=1, handlelength=4, numpoints=1)
        ax.set_title(plot_dict_i['title'])

        plt.savefig(os.path.join('./pdfs/', '{}_curve1_{}.pdf'.format(scenario, plot_dict_i["variable"])), dpi=300)

        plt.show()
        i += 1


def prepare_data_2(dict_dynamic, case, tlim = 2*365):
    t1 = dict_dynamic[case]['condenser.k']['Times']
    plot_dict = [
        {
         'variable': 'condenser.k',
         'y_label': 'Cooling water flowrate per tube (kg/s)', 'leg_position': 'best', 'ylim': (0.45, 0.5),
         't1': t1[t1<tlim],
         'x1': dict_dynamic[case]['condenser.k']['Values'][t1<tlim,:,:],
         'color': "green",
         },
        {
         'variable': 'condenser.Rf',
         'y_label': 'Fouling resistance per tube (10$^{-3}$ m$^2$K/W)', 'leg_position': 'best', 'ylim': (0, 0.30),
         't1': t1[t1<tlim],
         'x1': dict_dynamic[case]['condenser.Rf']['Values'][t1<tlim,:,:] * 1e3,
         'color': "black",
         },
        {
         'variable': 'condenser.v',
         'y_label': 'Fluid velocity (m/s)', 'leg_position': 'best', 'ylim': (2.4, 2.9),
         't1': t1[t1<tlim],
         'x1': dict_dynamic[case]['condenser.v']['Values'][t1<tlim,:,:],
         'color': "blue",
         },
        {
         'variable': 'condenser.T',
         'y_label': 'Cooling water temperature (K)', 'leg_position': 'best', 'ylim': (286, 305),
         't1': t1[t1<tlim],
         'x1': dict_dynamic[case]['condenser.T']['Values'][t1<tlim,:,:],
         'color': "red",
         },

    ]

    return plot_dict


def prepare_data_2s(dict_dynamic, case, tlim = 2*365):
    t1 = dict_dynamic[case]['condenser.k']['Times']

    plot_dict = [
        {'variable': 'condenser.k','y_label': 'Cooling water flowrate per tube (kg/s)','leg_position': 'best', 'ylim': (0.1, 1),
        't1': t1[t1<tlim],
        'x1': dict_dynamic[case]['condenser.k']['Values'][t1<tlim,:,:],
        'color': "green",
        },
        {'variable': 'condenser.Rf','y_label': 'Fouling resistance per tube (10$^{-3}$ m$^2$K/W)','leg_position': 'best', 'ylim': (0, 0.30),
        't1': t1[t1<tlim],
        'x1': dict_dynamic[case]['condenser.Rf']['Values'][t1<tlim,:,:]*1e3,
        'color': "black",
        },
        {'variable': 'condenser.v','y_label': 'Fluid velocity (m/s)','leg_position': 'best', 'ylim': (2.4, 3.1),
        't1': t1[t1<tlim],
        'x1': dict_dynamic[case]['condenser.v']['Values'][t1<tlim,:,:],
        'color': "blue",
        },
        {'variable': 'condenser.T','y_label': 'Cooling water temperature (K)','leg_position': 'best', 'ylim': (280, 305),
        't1': t1[t1<tlim],
        'x1': dict_dynamic[case]['condenser.T']['Values'][t1<tlim,:,:],
        'color': "red",
        },

    ]

    return plot_dict


def plot_curves_2(plot_dict, ix_list, line_style_list, scenario='short-term'):
    i = 0
    for plot_dict_i in plot_dict:

        fig = plt.figure(figsize=(12, 4))

        ax = fig.add_subplot(121)
        for ix, line_style in zip(ix_list, line_style_list):
            ax.plot(plot_dict_i['t1'], plot_dict_i['x1'][:, 0, ix - 1], line_style, lw=2.5, label="z={}".format(ix))
        for ax in plt.gcf().axes:
            for line in ax.get_lines():
                line.set_color(plot_dict_i['color'])
        ax.set_xlabel('Time (days)')
        ax.set_ylabel(plot_dict_i['y_label'])
        if plot_dict_i['ylim']:
            ax.set_ylim(plot_dict_i['ylim'][0], plot_dict_i['ylim'][1])
        leg = plt.legend(frameon=False, loc=plot_dict_i['leg_position'], ncol=1, handlelength=4, numpoints=1)
        ax.set_title('Inlet')

        ax = fig.add_subplot(122)
        for ix, line_style in zip(ix_list, line_style_list):
            ax.plot(plot_dict_i['t1'], plot_dict_i['x1'][:, -1, ix - 1], line_style, lw=2.5, label="z={}".format(ix))
        for ax in plt.gcf().axes:
            for line in ax.get_lines():
                line.set_color(plot_dict_i['color'])
        ax.set_xlabel('Time (days)')
        ax.set_ylabel(plot_dict_i['y_label'])
        if plot_dict_i['ylim']:
            ax.set_ylim(plot_dict_i['ylim'][0], plot_dict_i['ylim'][1])
        leg = plt.legend(frameon=False, loc=plot_dict_i['leg_position'], ncol=1, handlelength=4, numpoints=1)
        ax.set_title('Outlet')


        plt.savefig(os.path.join('./pdfs/', '{}_curve2_{}.pdf'.format(scenario, plot_dict_i["variable"])), dpi=300)

        plt.show()
        i += 1


def prepare_data_3(dict_dynamic, case):
    plot_dict = [
        {
         'variable': 'condenser.Rf',
         'y_label': 'Fouling resistance per tube (10$^{-3}$ m$^2$K/W)', 'leg_position': 'lower left', 'ylim': (0, 0.4),
         'time': dict_dynamic[case]['condenser.Rf']['Times'],
         'x': dict_dynamic[case]['condenser.L']['Values'][0] * np.asarray(
             dict_dynamic[case]['condenser.Rf']['Domains'][0]),
         'y': dict_dynamic[case]['condenser.Rf']['Values'] * 1e3,
         'color': "black",
         },
        {
         'variable': 'condenser.v',
         'y_label': 'Fluid velocity (m/s)', 'leg_position': 'lower right', 'ylim': (2.4, 3.2),
         'time': dict_dynamic[case]['condenser.Rf']['Times'],
         'x': dict_dynamic[case]['condenser.L']['Values'][0] * np.asarray(
             dict_dynamic[case]['condenser.v']['Domains'][0]),
         'y': dict_dynamic[case]['condenser.v']['Values'],
         'color': "blue",
         },
        {
         'variable': 'condenser.T',
         'y_label': 'Cooling water temperature (K)', 'leg_position': 'lower right', 'ylim': (285, 305),
         'time': dict_dynamic[case]['condenser.T']['Times'],
         'x': dict_dynamic[case]['condenser.L']['Values'][0] * np.asarray(
             dict_dynamic[case]['condenser.T']['Domains'][0]),
         'y': dict_dynamic[case]['condenser.T']['Values'],
         'color': "red",
         },
        {
         'variable': 'condenser.mf',
         'y_label': 'Deposit per area (kg/m$^2$)', 'leg_position': 'lower left', 'ylim': (0, 0.30),
         'time': dict_dynamic[case]['condenser.mf']['Times'],
         'x': dict_dynamic[case]['condenser.L']['Values'][0] * np.asarray(
             dict_dynamic[case]['condenser.mf']['Domains'][0]),
         'y': dict_dynamic[case]['condenser.mf']['Values'],
         'color': "black",
         },

    ]

    return plot_dict


def plot_curves_3(plot_dict, line_style_list, it_list, scenario = "short-term"):
    i = 0
    for plot_dict_i in plot_dict:
        fig = plt.figure(figsize=(12, 4))

        ax = fig.add_subplot(131)
        for it, line_style in zip(it_list, line_style_list):
            ax.plot(plot_dict_i['x'], plot_dict_i['y'][it, :, 0], line_style, lw=2.5,
                    label="{} days".format(round(plot_dict_i['time'][it], 1)))
        for ax in plt.gcf().axes:
            for line in ax.get_lines():
                line.set_color(plot_dict_i['color'])
        ax.set_xlabel('Position (m)')
        ax.set_ylabel(plot_dict_i['y_label'])
        if plot_dict_i['ylim']:
            ax.set_ylim(plot_dict_i['ylim'][0], plot_dict_i['ylim'][1])
        leg = plt.legend(frameon=False, loc='best', ncol=1, handlelength=4, numpoints=1)
        ax.set_title('Tube profile for z=1')

        ax = fig.add_subplot(132)
        for it, line_style in zip(it_list, line_style_list):
            ax.plot(plot_dict_i['x'], plot_dict_i['y'][it, :, 3], line_style, lw=2.5,
                    label="{} days".format(round(plot_dict_i['time'][it], 1)))
        for ax in plt.gcf().axes:
            for line in ax.get_lines():
                line.set_color(plot_dict_i['color'])
        ax.set_xlabel('Position (m)')
        # ax.set_ylabel(plot_dict_i['y_label'])
        if plot_dict_i['ylim']:
            ax.set_ylim(plot_dict_i['ylim'][0], plot_dict_i['ylim'][1])
        leg = plt.legend(frameon=False, loc='best', ncol=1, handlelength=4, numpoints=1)
        ax.set_title('Tube profile for z=4')
        ax.set_yticklabels([])

        ax = fig.add_subplot(133)
        for it, line_style in zip(it_list, line_style_list):
            ax.plot(plot_dict_i['x'], plot_dict_i['y'][it, :, -1], line_style, lw=2.5,
                    label="{} days".format(round(plot_dict_i['time'][it], 1)))
        for ax in plt.gcf().axes:
            for line in ax.get_lines():
                line.set_color(plot_dict_i['color'])
        ax.set_xlabel('Position (m)')
        # ax.set_ylabel(plot_dict_i['y_label'])
        if plot_dict_i['ylim']:
            ax.set_ylim(plot_dict_i['ylim'][0], plot_dict_i['ylim'][1])
        leg = plt.legend(frameon=False, loc='best', ncol=1, handlelength=4, numpoints=1)
        ax.set_title('Tube profile for z=34')
        ax.set_yticklabels([])

        plt.savefig(os.path.join('./pdfs/', '{}_curve3_{}.pdf'.format(scenario, plot_dict_i["variable"])), dpi=300)

        plt.subplots_adjust(bottom=0.15, wspace=0.05)
        plt.show()
        i += 1

def plot_violins(dict_dynamic, case, variable, x2, y2,
                 x2title='Aprox. Film Thickness',
                 x2label='Thickness ($\mu$m)',
                 yname='Fouling resistance (10$^{-3}$ m$^2$K/W)',
                 ymin=0.0, ymax=0.16, iy_list=(0, -1),
                 color1='lightgray', color2='black', factor=1, scenario = "short-term"):

    iy_name_list = ('Inlet distribution', 'Outlet distribution')
    t = dict_dynamic[case][variable]['Times']
    z = np.asarray(dict_dynamic[case][variable]['Domains'][1])

    fig = plt.figure(figsize=(12, 4))

    i = 0
    for iy, iy_name in zip(iy_list, iy_name_list):

        ax = plt.subplot2grid((1, 3), (0, i), colspan=1)

        i += 1

        xtick_list = []
        all_data = []
        for ix in (0, 365+4, 2*365+4, 3*365+4, 4*365+4):
            all_data.append(np.transpose(dict_dynamic[case][variable]['Values'][ix, (iy,), :] * factor))
            xtick_list.append('\n{:6.1f}'.format(t[ix]))

        all_data = np.concatenate(all_data, axis=1)

        # plot violin plot
        parts = ax.violinplot(all_data, showmeans=False, showmedians=True)

        plt.setp(ax, xticks=[y + 1 for y in range(all_data.shape[1])],
                 xticklabels=xtick_list)
        if i == 1:
            ax.set_ylabel(yname)
        ax.set_xlabel('Time (days)')
        ax.set_ylim(ymin, ymax)
        ax.yaxis.grid()

        ax.set_title(iy_name)

        for partname in ('cbars', 'cmins', 'cmaxes', 'cmeans', 'cmedians'):
            if partname in parts:
                vp = parts[partname]
                vp.set_edgecolor(color2)
                vp.set_linewidth(1)

        for pc in parts['bodies']:
            pc.set_facecolor(color1)
            pc.set_edgecolor(color2)
            pc.set_alpha(1)

    ax.set_yticklabels([])

    ax = plt.subplot2grid((1, 3), (0, 2), colspan=1)

    ax.plot(x2, y2, '-', color=color2, lw=2.5)
    ax.set_xlabel(x2label)
    ax.set_title(x2title)
    for label in ax.get_xmajorticklabels() + ax.get_xmajorticklabels():
        label.set_rotation(90)
        label.set_horizontalalignment("center")
    ax.set_ylim(ymin, ymax)
    ax.xaxis.grid()
    ax.yaxis.grid()

    ax.set_yticklabels([])

    plt.subplots_adjust(bottom=0.15, wspace=0.05)

    caseaux = case.replace(" ","").lower()
    plt.savefig(os.path.join('./pdfs/', '{}_violin_{}.pdf'.format(scenario, variable)), dpi=300)

    plt.show()


def plot_contour(dict_dynamic, case, variable, xvariable, levels, color, title, ix_list=(0, 365+4, 2*365+4, 3*365+4, 4*365+4), factor=1,
                 scenario="short-term"):
    print(title)
    i = 0
    fig = plt.figure(figsize=(12, 3))

    for ix in ix_list:
        ax = fig.add_subplot(1, len(ix_list), i + 1)

        tA = dict_dynamic[case][variable]['Times']
        xA = np.transpose(dict_dynamic[case][variable]['Values'][ix, :, :]) * factor
        z0A = dict_dynamic[case][xvariable]['Values'][0] * np.asarray(dict_dynamic[case][variable]['Domains'][0])
        z1A = np.asarray(dict_dynamic[case][variable]['Domains'][1])
        Z0A, Z1A = np.meshgrid(z0A, z1A)

        CS = ax.contour(Z0A, Z1A, xA, levels, colors=color, linewidths=2.5)
        ax.clabel(CS, inline=1, fontsize=10)
        ax.set_title("day #{}".format(round(tA[ix], 1)))
        ax.set_xlabel('Position (m)')
        ax.set_ylabel('z (-)')
        ax.invert_yaxis()

        i += 1
    caseaux = case.replace(" ","").lower()
    plt.savefig(os.path.join('./pdfs/', '{}_contour_{}.pdf'.format(scenario, variable)), dpi=300)
    plt.show()

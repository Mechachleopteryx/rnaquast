import sys
import os

import numpy as np
import pandas
import matplotlib.pyplot as plt

max_degree = 2
postfix_g = "_gene"
postfix_i = "_transcript"
list_colors = ['blue', 'red', 'green', 'yellow', 'magenta', 'orange', 'cyan', 'black']

# read simulated data file
df_g = pandas.read_csv(sys.argv[1], delim_whitespace=True)
df_i = pandas.read_csv(sys.argv[2], delim_whitespace=True)

def generate_pathes(config_path):
    partial_paths_df = pandas.read_csv(config_path, header=None)

    paths_g50 = set(partial_paths_df[0].astype(str) + '.50%-assembled.genes')
    paths_g95 = set(partial_paths_df[0].astype(str) + '.95%-assembled.genes')
    paths_i50 = set(partial_paths_df[0].astype(str) + '.50%-assembled.isoforms')
    paths_i95 = set(partial_paths_df[0].astype(str) + '.95%-assembled.isoforms')

    return paths_g50, paths_g95, paths_i50, paths_i95

paths = generate_pathes(sys.argv[3])
paths_g50 = paths[0]
paths_g95 = paths[1]
paths_i50 = paths[2]
paths_i95 = paths[3]

def filter_by_assembled(path_assembled, df, postfix):
    # read 50 / 95%-assembled genes / isoforms
    good_transcripts_df = pandas.read_csv(path_assembled, header=None)
    good_transcripts = set(good_transcripts_df[0].str[0:-len(postfix)])
    df_filtered = df[df.transcript_id.isin(good_transcripts)]
    return df_filtered


def plot_coverage_plot(paths, df, postfix, name):
    plt.title('Cumulative plot')
    legend_text = []
    for i_path in range(len(paths)):
        path = paths[i_path]
        i_ext = os.path.basename(path).find('.')
        label = os.path.basename(path)[:i_ext]
        legend_text.append(label)

        bins = np.logspace(0, max_degree, max_degree + 1)

        df_filtered = filter_by_assembled(path, df, postfix)

        groups_by_TPM = df_filtered.groupby(np.digitize(df_filtered.TPM, bins))

        x = np.insert(bins, len(bins), 10 ** (max_degree + 1))
        plt.plot(x, np.cumsum(groups_by_TPM.size()), '.-', color=list_colors[i_path % len(list_colors)])
        # plt.ylim(0, len(df_filtered) + 100)
        plt.xscale('symlog')
        plt.yscale('log')

    plt.xlabel('TPM')
    plt.ylabel('Number')
    plt.legend(legend_text, fontsize='x-small', loc='center left', bbox_to_anchor=(1.01, 0.5))
    plt.savefig(name, additional_artists='art', bbox_inches='tight')
    plt.show()

def get_label(path):
    i_ext = os.path.basename(path).find('.')
    label = os.path.basename(path)[:i_ext]
    return label

def plot_FP(paths_g50, paths_g95, paths_i50, paths_i95,
            df_g, df_i, postfix_g, postfix_i, name):
    zero_cov_num_g = df_g[df_g.TPM == 0].shape[0]
    zero_cov_num_i = df_i[df_i.TPM == 0].shape[0]
    plt.title('FP histogram\n (zero coverage genes {}, isoforms {})'.
              format(zero_cov_num_g, zero_cov_num_i))
    legend_text = []
    x = np.array(range(4))
    for i_path in range(len(paths_g50)):
        legend_text.append(get_label(paths_g50[i_path]))

        df_filtered_g50 = filter_by_assembled(paths_g50[i_path], df_g, postfix_g)
        FP_g50 = df_filtered_g50[df_filtered_g50.TPM == 0].shape[0]

        df_filtered_g95 = filter_by_assembled(paths_g95[i_path], df_g, postfix_g)
        FP_g95 = df_filtered_g95[df_filtered_g95.TPM == 0].shape[0]

        df_filtered_i50 = filter_by_assembled(paths_i50[i_path], df_i, postfix_i)
        FP_i50 = df_filtered_i50[df_filtered_i50.TPM == 0].shape[0]

        df_filtered_i95 = filter_by_assembled(paths_i95[i_path], df_i, postfix_i)
        FP_i95 = df_filtered_i95[df_filtered_i95.TPM == 0].shape[0]

        plt.plot(x, [FP_g50, FP_g95, FP_i50, FP_i95], '.', color=list_colors[i_path % len(list_colors)])

    plt.xticks(x, ['50%-assembled\ngenes', '95%-assembled\ngenes',
                   '50%-assembled\nisoforms', '95%-assembled\nisoforms'])
    plt.ylabel('FP')
    plt.legend(legend_text, fontsize='x-small', loc='center left', bbox_to_anchor=(1.01, 0.5))
    plt.savefig(name, additional_artists='art', bbox_inches='tight')
    plt.show()

plot_coverage_plot(paths_g50, df_g, postfix_g, '50%-behavior.genes.png')
plot_coverage_plot(paths_g95, df_g, postfix_g, '95%-behavior.genes.png')
plot_coverage_plot(paths_i50, df_i, postfix_i, '50%-behavior.isoforms.png')
plot_coverage_plot(paths_i95, df_i, postfix_i, '95%-behavior.isoforms.png')

plot_FP(paths_g50, paths_g95, paths_i50, paths_g95, df_g, df_i, postfix_g, postfix_i, 'FP.png')
# ----------------------------------------------------------------------------
# Copyright (c) 2012-2018, American Gut Project development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import jinja2
import pkg_resources
import seaborn as sns
import matplotlib.pyplot as plt
from io import StringIO
import pandas as pd
import numpy as np


class Reporter:
    def __init__(self, alpha, beta, taxa, mf, feature_table, samples):

        # column names in the mapping file
        self.host_type = 'HOST_TYPE'
        self.host_subject_id = 'HOST_SUBJECT_ID'
        self.sample_type = 'SAMPLE_TYPE'

        self._alpha = alpha
        self._beta = beta
        self._taxa = taxa
        self._feature_table = feature_table

        self._mf = mf
        self._samples = set(samples)

    def plot_alpha(self, sample_type, subset):
        """

        Parameters
        ---------
        subset: list of str
            A list of samples to highlight in an alpha diversity plot.
        """

        if len(subset) > 1:
        # if more than 1 sample for the participant
        # distribution rotated 90deg. and line plot of alpha diversity over time

            fig, (ax1, ax2) = plt.subplots(1, 2, sharey=True)

            # create a line plot
            tiny_mf = self._mf.loc[subset].copy()
            tiny_mf['α'] = self._alpha[subset]
            tiny_mf['Time'] = pd.to_datetime(tiny_mf['collection_timestamp'],
                                             errors='coerce')
            main_plot = sns.pointplot(x="Time",
                                      y="α",
                                      data=tiny_mf,
                                      ax=ax2)

            for tick in ax2.get_xticklabels():
                tick.set_rotation(90)

        else:
        # Note: remember the subaxis plot
        # use distribution plot and add a vertical line indicating the sample
            fig, ax1 = plt.subplots(1)

        # distribution: all of AG for a given sample type
        # 1. subsample alpha vector
        sample_type_subset = self._mf[self._mf[self.sample_type] == sample_type].index
        alpha_sample_type = self._alpha.loc[sample_type_subset]
        # 2. plot
        ag_distplot = sns.distplot(alpha_sample_type, vertical=(len(subset)>1),
                                   hist=False, ax=ax1)

        imgdata = StringIO()
        fig.savefig(imgdata, format='svg')
        imgdata.seek(0)  # rewind the data

        svg_data = imgdata.getvalue()  # this is svg data

        # return a plot (SVG)
        return svg_data

    def plot_beta(self, subset, area = 20, subject_color = 'red'):
        """

        Parameters
        ---------
        subset: list of str
            A list of samples to highlight in an beta diversity plot.
        """
        # makes a scatter plot based on pc1, pc2 and colored by body site
        # highlights the subset of samples

        fig, ax = plt.subplots(1)

        body_sites = self._mf[self.sample_type].unique()
        colors = np.random.rand(len(body_sites), 3)

        # general distribution
        # colored by body site
        for i, body_site in enumerate(body_sites):
            body_site_subset = self._beta.samples.loc[self._mf[self._mf[self.sample_type] == body_site].index]

            ax.scatter(body_site_subset[0], body_site_subset[1],
                       s=area,
                       c=colors[i])

        # highlight samples
        highlight_subset = self._beta.samples.loc[subset]

        ax.scatter(highlight_subset[0], highlight_subset[1],
                   s=area**2, c=subject_color, alpha=0.9)

        imgdata = StringIO()
        fig.savefig(imgdata, format='svg')
        imgdata.seek(0)  # rewind the data

        svg_data = imgdata.getvalue()  # this is svg data

        # return a plot (SVG)
        return svg_data

    def summarize_taxa(self, sample_type, subset):
        """Report most abundant and enriched microbes in subject's sample.

        Parameters
        ---------
        sample_type: str
            Specify sample type we summarize over.
        subset: list of str
            A list of samples to highlight in an alpha diversity plot.
        """
        # most enriched microbes
        # 1. calculate population-average proportion of microbes
        sample_type_subset = self._mf[self._mf[self.sample_type] == sample_type].index

        feature_table_sample_type = self._feature_table.filter(sample_type_subset,
                                                               inplace=False)

        #TODO
        # prune BIOM table to remove empty features

        # find most prevalent microbes
        presence_absence_table = feature_table_sample_type.pa()
        f = lambda x, y: x+y
        prevalence = pd.Series(presence_absence_table.reduce(f, 'observation'),
                               index=presence_absence_table.ids(axis='observation'))

        subset_feature_table = feature_table_sample_type.filter(subset,
                                                                axis='sample',
                                                                invert=False,
                                                                inplace=False)
        # remove 0 features
        subset_feature_table.remove_empty(axis='observation', inplace=True)
        subset_features = subset_feature_table.ids(axis='observation')

        subset_prevalence = prevalence[subset_features].sort_values()

        # replace UUIDs with taxonomy
        subset_prevalence_wtax = pd.Series(subset_prevalence.values,
                                           index=self._taxa[subset_prevalence.index].values)

        most_popular = subset_prevalence_wtax[-5:]
        most_unique = subset_prevalence_wtax[:5]

        most = most_popular.to_frame().to_html() + most_unique.to_frame().to_html()

        #TODO
        # most abundant microbes in the population


        # return an HTML-formatted Pandas dataframe
        return most

    def iter_sample_types(self, subject_sub):
        """Iterate over the sample types in a subject's dataframe

        Parameters
        ----------
        subset : pd.DataFrame
            A metadata subset for a subject's (implying subject identifier
            and subject type) samples. This is usually as generated by the
            iter_subjects method.

        Yields
        ------
        str
            At every iteration yields the unique sample types for this subject.
        pd.DataFrame
            The subset of the metadata corresponding to each subject's
            sample types.
        """
        for sample_type, st_subset in subject_sub.groupby([self.sample_type]):
            yield sample_type, st_subset

    def iter_subjects(self):
        """Iterate over the subject ids and subject types in the metadata

        Yields
        ------
        str
            The subject's identifier, as described by the column in
            ``self.host_subject_id``.
        str
            The subject's host type, as described by the column in
            ``self.host_type``.
        pd.DataFrame
            The subset of the metadata corresponding to each subject's samples.
        """
        _mf = self._mf.loc[self._feature_table.ids()].copy()
        # expects to yield the subject ids and subject types
        sub = _mf.loc[self._samples].copy()

        for vals, df in sub.groupby([self.host_subject_id, self.host_type]):
            host_subject_id, host_type = vals
            yield host_subject_id, host_type, df


class ReporterView:
    template_for_plots = 'plot-grid.html'

    def __init__(self, reporter):
        path = pkg_resources.resource_filename('q2_american_gut',
                                               'assets/report/')

        loader = jinja2.FileSystemLoader(searchpath=path)
        environment = jinja2.Environment(loader=loader)

        self.plot_grid = environment.get_template('plot-grid.html')

        self.reporter = reporter

    def render_plots(self, sample_type, sample_type_subset):

        s = sample_type_subset.index.tolist()

        taxa = self.reporter.summarize_taxa(sample_type, s)
        beta = self.reporter.plot_beta(s)
        alpha = self.reporter.plot_alpha(sample_type, s)

        # create a template of some sort with all these things
        return self.plot_grid.render(taxa=taxa, beta=beta, alpha=alpha)

    def site_translator(self, site_name):
        # translate between category names and emojis
        # eg oral -> *tongue emoji*

        return '?'

# ----------------------------------------------------------------------------
# Copyright (c) 2012-2018, American Gut Project development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------


class Reporter:
    def __init__(alpha, beta, taxa, mf, samples):

        # make public properties for:
        # host_type
        # host_subject_id
        # sample_type

        # make private properties for:
        # alpha vector
        # beta pcoa
        # taxa table
        # mapping file
        # samples
        pass

    def plot_alpha(self, subset, category, category_value):
        """

        Parameters
        ---------
        subset: list of str
            A list of samples to highlight in an alpha diversity plot.
        category: str
            Metadata column to search for ``category_value``.
        category_value: str
            Value in the metadata column to subset the data by.
        """

        # if there's more than one sample:
        #      create a line plot
        #
        #     Note: remember the subaxis plot
        # else:
        #      create a distribution plot.
        #

        # return a plot (SVG)
        return None

    def plot_beta(self, subset):
        """

        Parameters
        ---------
        subset: list of str
            A list of samples to highlight in an alpha diversity plot.
        """
        # makes a scatter plot based on pc1, pc2 and colored by body site
        # highlights the subset of samples

        # return a plot (SVG)
        return None


    def summarize_taxa(self, subset):
        """

        Parameters
        ---------
        subset: list of str
            A list of samples to highlight in an alpha diversity plot.
        """
        # reuses whatever was on the latex thing

        # return an HTML-formatted Pandas dataframe
        return None

    def get_subset(self, host_type_value, host_subject_id_value,
                   sample_type_value):
        """
        Parameters
        ----------
        host_type_value: str
            Wat?
        host_subject_id_value: str
            Wat?
        sample_type_value: str
            Wat?

        """
        # should be a sample subset for the category values
        return []


class ReporterView:
    def __init__(reporter):
        # define a property for
        #       display_template: thing that contains alpha, beta and taxa
        #       page_template: thing that contains multiple display_templates
        #       the reporter
        pass

    def display(self):
        # this is all pseudocode:
        #
        # for host_type in self.reporter.hosts:
        #     for host_subject_id in self.reporter.host_types:
        #         for sample_type in self.reporter.sample_types:
        #             pass
        pass

    def site_translator(self, site_name):
        # translate between category names and emojis
        # eg oral -> *tongue emoji*

        return '?'

# ----------------------------------------------------------------------------
# Copyright (c) 2012-2018, American Gut Project development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import os.path
import pkg_resources
import shutil
import skbio
import biom

import pandas as pd
import numpy as np
import q2templates

from qiime2 import Metadata
from scipy.stats import gaussian_kde


TEMPLATES = pkg_resources.resource_filename('q2_american_gut', 'assets')


def report(output_dir: str,
           pcoa: skbio.OrdinationResults,
           metadata: Metadata,
           alpha: pd.Series,
           table: biom.Table,
           taxonomy: pd.Series,
           samples: list) -> None:
    metadata = metadata.to_dataframe()
    DATA = {}

    _insanity_checker(samples, metadata, table, alpha, pcoa)

    DATA.update(_compute_alpha(alpha, samples))

    index = os.path.join(TEMPLATES, 'report', 'index.html')
    q2templates.render(index, output_dir, context={'name': 'foo',
                                                   'DATA': DATA})

    # Copy assets for rendering figure
    shutil.copytree(os.path.join(TEMPLATES, 'report', 'resources'),
                    os.path.join(output_dir, 'resources'))


def _insanity_checker(samples, metadata, table, alpha, pcoa):
    '''
    Check if all of the data required by the plugin contains the samples
    provided for analysis. Objects themselves need to be Q2-compliant, so there
    is no need to sanity check them.

    Raises
    ------
    ValueError
        if any object is missing samples provided by `samples`
    '''

    samples = set(samples)

    if not samples.issubset(set(metadata.index)):
        raise ValueError('There are missing samples in the metadata')
    if not samples.issubset(set(table.ids('sample'))):
        raise ValueError('There are missing samples in the BIOM table')
    if not samples.issubset(alpha.index):
        raise ValueError('There are missing samples in the alpha diversity '
                         'vector')
    if not samples.issubset(set(pcoa.samples.index)):
        raise ValueError('There are missing samples in the ordination')


def _compute_alpha(alpha, samples):
    '''
    this function gets data in a format that we can put it in a json document
    1. KDE
    2. pull out a-div values for samples of interest

    based on:
    https://glowingpython.blogspot.com/2012/08/kernel-density-estimation-with-\
    scipy.html

    Returns
    -------
    alpha_kde : dict
        alpha_kde_x
        alpha_kde_y
        alpha_markers
    '''
    x = np.linspace(alpha.min(), alpha.max(), 100)
    y_density = gaussian_kde(alpha)(x)
    y = y_density * len(alpha)

    markers = alpha.loc[samples].to_dict()

    alpha_kde = {'alpha_kde_x': x.tolist(),
                 'alpha_kde_y': y.tolist(),
                 'alpha_markers': markers}

    return alpha_kde

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

from ._reports import Reporter, ReporterView

TEMPLATES = pkg_resources.resource_filename('q2_american_gut', 'assets')


def report(output_dir: str,
           pcoa: skbio.OrdinationResults,
           metadata: Metadata,
           alpha: pd.Series,
           table: biom.Table,
           taxonomy: pd.Series,
           samples: list) -> None:
    DATA = {}
    q2_metadata = metadata

    metadata = metadata.to_dataframe()
    _insanity_checker(samples, metadata, table, alpha, pcoa)

    # instantiate the reporter
    rep = Reporter(alpha, pcoa, taxonomy, metadata, table, samples)

    # instantiate the reporter view
    reporter_view = ReporterView(rep)

    index = os.path.join(TEMPLATES, 'report', 'index.html')
    q2templates.render(index, output_dir,
                       context={'reporter_view': reporter_view, 'DATA': DATA})

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

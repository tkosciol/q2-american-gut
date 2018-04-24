# ----------------------------------------------------------------------------
# Copyright (c) 2012-2018, American Gut Project development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import unittest
import pandas as pd
import biom
import numpy as np

from skbio import OrdinationResults
from q2_american_gut._visualizer import _insanity_checker, _compute_alpha


class AGReportTests(unittest.TestCase):
    def setUp(self):
        self.alpha = pd.Series([1, 2, 3], index=list('abc'))

        self.data = np.asarray([[0, 0, 1], [1, 3, 42]])
        self.biom = biom.Table(self.data, ['O1', 'O2'], ['a', 'b', 'c'])

        self.eigvals = [0.51236726, 0.30071909, 0.26791207]
        self.proportion_explained = [0.2675738328, 0.157044696, 0.1399118638]
        self.sample_ids = ['a', 'b', 'c']
        self.axis_labels = ['PC%d' % i for i in range(1, 4)]
        np.random.seed(11)
        data = np.random.randn(3, 3)

        expected_results = OrdinationResults(
            short_method_name='PCoA',
            long_method_name='Principal Coordinate Analysis',
            eigvals=pd.Series(self.eigvals, index=self.axis_labels),
            samples=pd.DataFrame(
                data,
                index=self.sample_ids, columns=self.axis_labels),
            proportion_explained=pd.Series(self.proportion_explained,
                                           index=self.axis_labels))
        self.ordination = expected_results

        self.metadata = pd.DataFrame(data=[[':0', ':)', ':/'],
                                           [':D', 'xD', '<3'],
                                           [';L', ']:->', ':S']],
                                     index=list('abc'),
                                     columns=['foo', 'bar', 'baz'])

    def test_insanity_checks_metadata_error(self):
        wrong_samples = list('bcd')
        with self.assertRaises(ValueError):
            _insanity_checker(wrong_samples,
                              self.metadata,
                              self.biom,
                              self.alpha,
                              self.ordination)

    def test_insanity_checks_biom_error(self):
        wrong_biom = biom.Table(self.data, ['O1', 'O2'],
                                ['b', 'c', 'd'])
        with self.assertRaises(ValueError):
            _insanity_checker(self.sample_ids,
                              self.metadata,
                              wrong_biom,
                              self.alpha,
                              self.ordination)

    def test_insanity_checks_alpha_error(self):
        wrong_alpha = pd.Series([1, 2, 3], index=list('bcd'))
        with self.assertRaises(ValueError):
            _insanity_checker(self.sample_ids,
                              self.metadata,
                              self.biom,
                              wrong_alpha,
                              self.ordination)

    def test_insanity_checks_ordination_error(self):
        sample_ids = list('bcd')
        data = np.random.randn(3, 3)
        wrong_results = OrdinationResults(
            short_method_name='PCoA',
            long_method_name='Principal Coordinate Analysis',
            eigvals=pd.Series(self.eigvals, index=self.axis_labels),
            samples=pd.DataFrame(
                data,
                index=sample_ids, columns=self.axis_labels),
            proportion_explained=pd.Series(self.proportion_explained,
                                           index=self.axis_labels))
        wrong_ordination = wrong_results

        with self.assertRaises(ValueError):
            _insanity_checker(self.sample_ids,
                              self.metadata,
                              self.biom,
                              self.alpha,
                              wrong_ordination)

    def test_sanity_checker(self):
        samples = ['a', 'b', 'c']
        _insanity_checker(samples,
                          self.metadata,
                          self.biom,
                          self.alpha,
                          self.ordination)
        samples = ['a']
        _insanity_checker(samples,
                          self.metadata,
                          self.biom,
                          self.alpha,
                          self.ordination)

    def test_compute_alpha(self):
        res = _compute_alpha(self.alpha, self.sample_ids)
        self.assertEqual(res['alpha_markers'], {'a': 1,
                                                'b': 2,
                                                'c': 3})
        self.assertEqual(min(res['alpha_kde_x']), 1)
        self.assertEqual(max(res['alpha_kde_x']), 3)
        self.assertEqual(len(res['alpha_kde_x']), 1000)
        self.assertEqual(len(res['alpha_kde_y']), 1000)


if __name__ == "__main__":
    unittest.main()

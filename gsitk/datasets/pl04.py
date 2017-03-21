"""
Processing of the PL04 dataset.

URL:
http://www.cs.cornell.edu/people/pabo/movie-review-data/
REF:
B. Pang, L. Lee, S. Vaithyanathan
Thumbs up?: sentiment classification using machine learning techniques
Proceedings of the ACL-02 conference on empirical methods in natural language processing-Volume 10, 
Association for Computational Linguistics (2002), pp. 79–86
"""

import os
import logging
import pandas as pd
import numpy as np
from glob import glob
from gsitk import config
from gsitk.datasets import utils
from gsitk.datasets.datasets import Dataset
from gsitk.preprocess import normalize

logger = logging.getLogger(__name__)


NAME = os.path.splitext(os.path.basename(__file__))[0]
fold_limits = zip(np.arange(0, 1000, 100), np.arange(99, 1000, 100))
folds = {i+1: limit  for i, limit in enumerate(fold_limits)}


class Pl04(Dataset):

    def __init__(self, info=None):
        if info is None:
            info = utils.load_info(NAME)
        super(Pl04, self).__init__(info)

    def _read_file(self, path, binary=False):
        with open(path, 'r') as f:
            content = f.read()
        return content

    def _get_file_cv_id(self, path):
        filename = os.path.splitext(os.path.basename(path))[0]
        id_ = filename.split('_')[-1]
        cv = filename.split('_')[0]
        cv = cv.replace('cv', '')
        return cv, id_
    
    def _choose_fold(self, cv, folds):
        cv = int(cv)
        for i, limits in folds.items():
            if cv >= limits[0] and cv <= limits[1]:
                return i

    def normalize_data(self):
        dataset = pd.DataFrame(columns=['id', 'fold', 'text', 'polarity'])
        data_path = os.path.join(config.DATA_PATH, self.name)
        raw_data_path = os.path.join(data_path,
                                     self.info['properties']['data_file'])
        logger.debug('Normalizing PL04')
        get_pol = lambda p: 1 if p == 'pos' else -1
        count = 0
        for pol in ('pos', 'neg'):
            for file in glob(os.path.join(raw_data_path, '{}/*'.format(pol))):
                text = self._read_file(file)
                cv, id_ = self._get_file_cv_id(file)
                fold = self._choose_fold(cv, folds)
                polarity = get_pol(pol)
                dataset.loc[count, :] = [id_, fold, text, polarity]
                count += 1
        normalized_text = normalize.normalize_text(dataset)
        dataset['text'] = normalized_text
        return dataset

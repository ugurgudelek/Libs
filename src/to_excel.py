import pandas as pd
import os

from analyzer import Analyzer
from config import Config
from database import Database

locname = 'adana-old'

output_path = '../output'
path = os.path.join(output_path,'samples',locname)

config = Config('../config.ini')
analyzer = Analyzer(config=config, database=Database(config))

intensities_dict = dict()
nm = None
for foldername in os.listdir(path):
    samples = analyzer.read_samples(os.path.join(path, foldername))
    samples = analyzer.validate_samples(samples)
    sample = analyzer.mean(samples)

    intensities_dict[int(sample.name.split("\\")[-1])] = sample.sample['intensities']
    if nm is None:
        nm = sample.sample['wavelengths'].values



intensities_df = pd.DataFrame.from_dict(intensities_dict)
intensities_df.index = nm


intensities_df.to_excel(os.path.join(output_path, 'sample_to_xlsx', '{}.xlsx'.format(locname)))
print()

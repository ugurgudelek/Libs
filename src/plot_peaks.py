from database import Database
from analyzer import Analyzer
from config import Config
import matplotlib.pyplot as plt

config = Config('../config.ini')
database = Database(config=config)
analyzer = Analyzer(config=config, database=database)

(sample, matches) = analyzer.process_samples('../output/samples/adana/1')


# Plot
fig, ax = plt.subplots()

analyzer.plot_data(ax, point_peaks=True, draw_verticals=False)
analyzer.plot_matches(ax)

ax.legend()
plt.show()

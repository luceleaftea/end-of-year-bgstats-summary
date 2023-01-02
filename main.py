from pathlib import Path

from general_summary import *
from flesh_and_blood_summary import *

general_summary(Path(__file__).parent / "./year.bgsplay")
flesh_and_blood_summary(Path(__file__).parent / "./year_fab.bgsplay")
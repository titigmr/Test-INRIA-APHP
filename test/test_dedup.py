
import sys
sys.path.append("..")
from utils.deduplicate import Duplication
import pandas as pd

def test_removed_one():
    df = pd.DataFrame({'given_name': ['josjua', 'joshua', 'vanessa', 'thierry'],
                       'surname': ["whiite", "white", 'bristow', 'ekers'],
                       'state': ["nsw", 'nsw', 'qld', 'nsw']})
    dupli = Duplication()
    dupli.detect_duplicates(df)
    assert dupli.removed == 0.25


def test_no_removed():
    df = pd.DataFrame({'given_name': {1: 'joshua', 2: 'alice', 3: 'sienna', 4: 'joshua', 5: 'ky'},
                       'surname': {1: 'elrick', 2: 'conboy', 3: 'craswell', 4: 'bastiaans', 5: 'laing'},
                       'address_1': {1: 'andrea place', 2: 'mountain circuit', 3: 'cumberlegeicrescent', 4: 'lowrie street', 5: 'nyawi place'},
                       'state': {1: 'nsw', 2: 'nsw', 3: 'wa', 4: 'nsw', 5: 'qld'}})

    dupli = Duplication()
    dupli.detect_duplicates(df)
    assert dupli.removed == 0
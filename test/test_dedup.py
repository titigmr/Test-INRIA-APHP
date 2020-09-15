from ..utils.deduplicate import Duplication
import pandas as pd

def test_removed_one():
    df = pd.DataFrame({'given_name': ['josjua', 'joshua', 'vanessa', 'thierry'],
                       'surname': ["whiite", "white", 'bristow', 'ekers'],
                       'state': ["nsw", 'nsw', 'qld', 'nsw']})
    dupli = Duplication()
    dupli.detect_duplicates(df)
    assert dupli.removed == 0.25


def test_no_removed():
    df = pd.DataFrame({'given_name': ['joshua','alice','sienna','joshua','ky'],
                       'surname': ['elrick','conboy','craswell','bastiaans','laing'],
                       'address_1': ['andrea place','mountain circuit','cumberlegeicrescent',
                       'lowrie street','nyawi place'],
                       'state': ['nsw', 'nsw','wa','nsw','qld']})

    dupli = Duplication()
    dupli.detect_duplicates(df)
    assert dupli.removed == 0


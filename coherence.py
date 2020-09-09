import pandas as pd
import numpy as np
from difflib import SequenceMatcher
from fuzzywuzzy import process

def convert_to_date(value):
    """
    Convert a float value to a datetime format. 
    If the date isn't convertible, return the date in string.
    """
    
    if not(np.isnan(value)):
        str_date = str(int(value))
        try :
            return pd.to_datetime(str_date, format='%Y%m%d')
        except : 
            return str_date


def calculate_age(date:pd.Series, year:int):
    """
    Calculate the age from the year of a date of birth 
    pandas serie.
    """
    date.fillna(0, inplace=True)
    date = date.apply(lambda x : int(str(int(x))[:4]))
    date = date.replace({0:None})
    return year - date


def gestalt_pattern_matching(a: str, b: str):
    """
    Find similarity between two string 
    using the gestalt pattern matching algorithm.
    """
    return SequenceMatcher(None, a, b).ratio()


def find_best_similar_levenstein(serie: pd.Series, dict_ref: dict):
    """
    Find the most similar value, with the levenstein distance, between values 
    in a pandas serie and a dictionary values. 
    Return a dictionnary where keys are values find in the serie and value is
    the most similar match.
    """
    closest_value = {}

    all_values = set(serie.values)
    all_values.remove(None)

    for i in all_values:
        value_close = process.extractOne(i, dict_ref.values())
        closest_value[i] = value_close[0]
    
    return closest_value

def find_best_similar(serie: pd.Series, dict_ref: dict, similarity, apply=True):
    """
    Find for each value on a pandas serie the most similar string from a dictionary referential. 
    This function use a function similarity (jaro-winkler, gestalt pattern matching for example).
    
    Return 
    ------
    serie : if apply is True, return the serie with most similar values computed
    closest_value : if apply is False, return the dictionary of similarity for each value 
    """
    
    all_values = set(serie.values)
    all_values.remove(None)

    closest_value = {}

    for data in all_values:
        best_ratio = 0

        for value in dict_ref.values():
            ratio = similarity(value.lower(), data)

            if ratio >= best_ratio:
                best_ratio = ratio
                value_close = value

        closest_value[data] = value_close
    
    if apply:
        return serie.replace(closest_value)
    else:
        return closest_value



def postcode_coherence(serie: pd.Series, ref_postcode: dict, str_postcode: list):
    """
    Find the state attributed for each value in a pandas serie.
    This function use a dictonary where keys is the state, and value is a numpy 
    array with all postcode in this state. The variable str_postcode is the list 
    of value where postcode is not integers.
    """
    def convert_postcode_toint(serie: pd.Series, str_postcode: list):
        serie.replace({i:None for i in str_postcode}, inplace=True)
        serie.fillna(0, inplace=True)
        serie = serie.astype(int)
        return serie

    def attribute_state(x, ref_postcode: dict):
        for key, value in ref_postcode.items():
            if x in value:
                return key

    new_serie = convert_postcode_toint(serie, str_postcode)

    post_code_serie = new_serie.apply(
        attribute_state, ref_postcode=ref_postcode)
    return post_code_serie


def correct_typo(serie: pd.Series, confidence=90, threshold=10):
    """
    Correct typographie errors between values find more than the threshold and 
    unique values in a pandas serie. The confidence is the ratio of similarity used by 
    the algortjm of matching (levenshtein distance).
    """
    typo_corrected = {}
    indice_lonely = serie.value_counts()[serie.value_counts() == 1].index
    infice_wright = serie.value_counts()[serie.value_counts() > threshold].index

    for i in indice_lonely:
        b_extract = process.extractOne(i, infice_wright)
        if b_extract[1] > confidence:
            typo_corrected[i] = b_extract[0]
            
    return typo_corrected


def apply_coherence(dataframe: pd.DataFrame, table="patient"):
    """
    Clean dataframe
    """
    if table == 'patient':
        pass

    elif table == 'pcr':
        dataframe.pcr = dataframe.pcr.replace(
            {'Negative': 'N', 'Positive': 'P'})

        return dataframe


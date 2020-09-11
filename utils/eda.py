import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def apply_gender(all_gender, threshold=0.7, apply=None):
    sexe = {}
    for giv in all_gender:
        name = giv["name"]
        prob = giv["probability"]
        if prob > threshold:
            gender = giv["gender"]
        else :
            gender = None
        
        sexe[name] = gender
    
    if apply is not None:
        assert type(apply) == pd.Series 
        serie = apply.replace(sexe)
        return serie
    else : 
        return sexe


def plot_na(pourc_na, df, color=None):
    plt.figure(figsize=(12, 8))
    plt.title('Part des NA pour chaque variable – Table Patient')
    plt.barh(df.columns, pourc_na,
             color=color)
    plt.xlabel('Pourcentage de valeurs manquantes')
    plt.ylabel('Variables')

    for i, v in enumerate(pourc_na):
        plt.text(v, i+0.2, " "+str(round(v, 2))+"%", color='blue', va='center')


def find_truth_age(age_re, age_es):
    """
    Get two values and return the group age associated. 
    If this two values are too differents, return None
    """
    
    def group_age(value: float):
        """
        Compute a float values for a group interval string.
        """
        if value <= 14:
            return '0-14'
        elif (value >= 15) and (value <= 44):
            return '15-44'
        elif (value >= 45) and (value <= 64):
            return '45-64'
        elif (value >= 65) and (value <= 84):
            return '65-84'
        elif (value >= 85) and (value <= 1):
            return '85-110'
        else :
            return 'extrem'
    

    g_age_re = group_age(age_re)
    g_age_es = group_age(age_es)

    if (g_age_es == g_age_re) and not((np.isnan(age_re))) and not((np.isnan(age_es))):
        f_age = g_age_re
    elif np.isnan(age_es):
        f_age = g_age_re
    elif np.isnan(age_re):
        f_age = g_age_es
    else:
        f_age = None
    
    return f_age

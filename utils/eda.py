import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def apply_gender(all_gender, threshold=0.7, apply_on=None):
    sexe = {}
    for giv in all_gender:
        name = giv["name"]
        prob = giv["probability"]
        if prob > threshold:
            gender = giv["gender"]
        else :
            gender = None
        
        sexe[name] = gender
    
    if apply_on is not None:
        serie = apply_on.replace(sexe)

        all_unique_val = serie.unique()
        verif = ~((all_unique_val == "male") | 
          (all_unique_val == "female") | 
          (all_unique_val == None))
        
        other_name = {i:None for i in all_unique_val[verif]}
        serie = serie.replace(other_name)
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


def match_state(s, p):
    """
    Match two values. If one of them is None return the second value. 
    Else, if they don't match return None.
    """
    if s is None:
        return p
    elif p is None:
        return s
    elif (s == p):
        return s
    else:
        return None


def plot_map(data, var, cmap='Blues', size_fig=(14, 8), 
             vminmax=(10, 3000), title='', anno_state=True, 
             anno_value=True, color_font='black'):
    """
    Plot map with a geodataframe and one column with values computed for each state.
    """

    fig, ax = plt.subplots(figsize=size_fig)
    data.plot(var,
              cmap=cmap,
              linewidth=0.8, edgecolor='0.8', ax=ax)
    
    sm = plt.cm.ScalarMappable(cmap=cmap,
                               norm=plt.Normalize(vmin=vminmax[0], vmax=vminmax[1]))
    cbar = fig.colorbar(sm)
    
    ax.annotate('Source Map: Commonwealth of Australia',
                xy=(0.1, .08), xycoords='figure fraction',
                horizontalalignment='left', verticalalignment='top',
                fontsize=10, color='#555555')
    
    if anno_state:
        data.apply(lambda x: ax.annotate(s=x.STATE_CODE,
                                         xy=x.geometry.centroid.coords[0],
                                         ha='center', size=10, fontweight='bold', 
                                         color=color_font), axis=1)
    if anno_value:
        data.apply(lambda x: ax.annotate(s=x[var],
                                         xy=(x.geometry.centroid.coords[0][0],
                                             x.geometry.centroid.coords[0][1]-2),
                                         ha='center', size=10, color=color_font), axis=1)
    ax.axis('off')
    ax.set_title(title)

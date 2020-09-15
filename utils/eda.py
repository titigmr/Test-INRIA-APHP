import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def apply_gender(all_gender, threshold=0.7, apply_on=None):
    """
    Create a dictionary where keys are the given name 
    and the values are the gender predicted by the output of genderize API.

    Parameters
    ---------
    all_gender : genderize api return (list of dict)
    threshold : confidence threshold for retaining the gender prediction
    apply_on : pandas series of names for which gender is predicted
    """
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
    """
    Plot NA from a dataframe in percentage for each column.

    Parameters 
    ----------
    pourc_na : list, values in percentage
    df : dataframe 
    """
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
    Take two values and return the associated group age. 
    If these values are different, return None.

    Parameters 
    ----------

    age_re : float, age informed
    age_es : float, age estimated by year of birth
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
            return None
    
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
    Else return None if they don't match.

    Parameters 
    ---------
    s : value one
    p : value two

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
             vminmax=(None,None), title='', anno_state=True, 
             anno_value=True, color_font='black', ax=None, fig=None, size_colorbar=1):
    """
    Plot map from a geodataframe containing the values to be ploted.

    Parameters 
    ----------
    data : pd.DataFrame, data
    var : str, variable selected
    cmap : str, palette color
    size_fig : tuple, size figure
    vminmax : tuple, default (None, None), range values for color bar
    title : str, title of graph
    anno_state : bool, show state names
    anno_value : bool, show values 
    color_font : str, font color
    ax : ax object, default is None
    fig : fig object, default is None
    size_colorbar : float, shrink color bar
    """
    if not all(vminmax):
        vminmax = (data[var].min(), data[var].max())
    
    if ax is None :
        fig, ax = plt.subplots(figsize=size_fig)

    sm = plt.cm.ScalarMappable(cmap=cmap, 
        norm=plt.Normalize(vmin=vminmax[0], vmax=vminmax[1]))
    cbar = fig.colorbar(sm, ax=ax, shrink=size_colorbar)
    
    data.plot(var,
              cmap=cmap,
              linewidth=0.8, edgecolor='0.8', ax=ax)
    
    if anno_state:
        data.apply(lambda x: ax.text(s=x.STATE_CODE,
                                         x=x.geometry.centroid.coords[0][0],
                                         y=x.geometry.centroid.coords[0][1]+2,
                                         ha='center', size=10, fontweight='bold', 
                                         color=color_font), axis=1)
    if anno_value:
        data.apply(lambda x: ax.text(s=x[var],
                                         x=x.geometry.centroid.coords[0][0], 
                                         y=x.geometry.centroid.coords[0][1],
                                         ha='center', size=10, color=color_font), axis=1)
    ax.axis('off')
    ax.set_title(title)



def plot_bar_PN(df_N, df_P, var, title='', 
                y=0, x=0, figsize=(12,4), 
                sort=True, print_none=True, ax=None):
    """
    Plot two bar graphs from two dataframes (positive and negative pcr test).

    Parameters
    ----------
    df_N : pd.Dataframe, dataframe where column pcr is negative
    df_P : pd.Dataframe where column pcr is positive
    var : str, selected columns
    sort : bool, sort bar
    print_none : bool, show NA bar
    ax : ax object, default None
    """
    if print_none : 
        df_N = df_N.replace(np.nan, "None") 
        df_P = df_P.replace(np.nan, "None")
    
    count_N = df_N[var].value_counts()
    count_P = df_P[var].value_counts()
    
    if sort:
        count_N = count_N.sort_index()
        count_P = count_P.sort_index()
    
    b = (0.45, 0.61, 0.8)
    r = (0.64, 0.2, 0.17)
    
    
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    
    ax.set_ylabel("Nombre de tests")
    
    ax.bar(x=count_N.index,
            height=count_N, color=b, width=0.5, label='Negative')
    ax.bar(x=count_P.index,
            height=count_P, color=r, width=0.5, label='Positive')
    ax.legend()
    
    ax.set_ylim(0,4000)
    ax.set_title(title)
    
    for i, v in enumerate(count_N.values):
        ax.text(i+x, v+y, s=str(v), color='black', fontweight='bold')

    for i, v in enumerate(count_P.values):
        ax.text(i+x , v+y, s=str(v), color='white', fontweight='bold')


def plot_crosstab(data, size=(12,8), ax=None, title=''):
    """
    Plot a heatmap from data crosstab.

    Parameters 
    -----------
    data : dataframe, pandas crosstab between two variables 
    size : tuple, size of graphic
    ax : ax object, default None
    title : str, name of graphic
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=size)
    sns.heatmap(data, cmap="Reds", ax=ax, annot=True, fmt='.1%', cbar=False)
    ax.set_title(title)


def plot_dist(df1, df2, size=(12,7), ax=None, bins=50, title="", label=('','')):
    """
    Plot a distribution by age and estimated age.

    Parameters
    -----------
    df1 : serie or list, age 
    df2 : serie or list, estimated age 
    size : tuple, size of figure
    bins : float, number of bins
    title : str, name of graph
    ax : ax object, default None 
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=size)
    
    sns.distplot(df1, bins=bins,
                 label=label[0], ax=ax)
    sns.distplot(df2, bins=bins, label=label[1], ax=ax)
    ax.set_title(title)
    ax.legend()


def plot_hist_age(df, ax=None, x=(0,0), y=(0,0), ylabel='', title=''):
    """
    Plot a histogram by age group for each test result (P or N).

    Parameters
    -----------
    x : tuple, label position of negative bar
    y : tuple, label position of positive bar
    ylabel : str, name of label
    title : str, name of graph
    ax : ax object, default None
    """
    b = (0.45, 0.61, 0.8)
    r = (0.64, 0.2, 0.17)

    d_a = df.groupby(['age_group', 'pcr'])['pcr'].count().unstack()

    d_a.plot.bar(color=(b,r), ax=ax, width=0.5)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    for i, v in enumerate(d_a.N.values):
        ax.text(i+x[0], v+x[1], s=str(v), color='black')

    for i, v in enumerate(d_a.P.values):
        ax.text(i+y[0] , v+y[1], s=str(v), color='black')
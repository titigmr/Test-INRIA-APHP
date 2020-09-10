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
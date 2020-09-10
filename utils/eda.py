import pandas as pd
import numpy as np


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

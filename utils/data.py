import numpy as np
from genderize import Genderize, GenderizeException
import json
import os

def get_postcode():
    """
    Return a dictionnary where state of Australia is the key 
    and the values is all postcode attributed.
    """
    return {"NSW": np.concatenate([np.arange(1000, 1999+1),
                                   np.arange(2000, 2599+1),
                                   np.arange(2619, 2899+1),
                                   np.arange(2921, 2999+1)]),

            "ACT": np.concatenate([np.arange(200, 299+1),
                                   np.arange(2600, 2618+1),
                                   np.arange(2900, 2920+1)]),

            "VIC": np.concatenate([np.arange(8000, 8999+1),
                                   np.arange(3000, 3999+1)]),

            "QLD": np.concatenate([np.arange(4000, 4999+1),
                                   np.arange(9000, 9999+1)]),

            "SA": np.arange(5000, 5999+1),

            "WA": np.concatenate([np.arange(6000, 6797+1),
                                  np.arange(6800, 6999+1)]),

            "TAS": np.arange(7000, 7999+1),

            "NT": np.arange(800, 999+1)}


def get_states():
    """
    Return a dictionnary where states of Australia are keys 
    and the values is the code for each state.
    """
    return {"South Australia":"SA",
            "Western Australia": "WA",
            "New South Wales": "NSW",
            "Queensland": "QLD",
            "Tasmania": "TAS",
            "Victoria": "VIC",
            "Northern Territory":"NT",
            "Australian Capital Territory":"ACT"}



def get_gender(unique_name):
    """
    Request genderize api to get the gender for each given name in a list.
    If maximum requests is done, return the last data stored.
    """
    try :
        get_gender = Genderize().get(unique_name)
        f = open("gender.json", "w") 
        json.dump(get_gender, f)
        f.close()
        return get_gender

    except GenderizeException:
        print("Request limit")
        if os.path.exists("gender.json"):
            with open('gender.json') as data_file:
                data_loaded = json.load(data_file)
            return data_loaded



from jellyfish import jaro_winkler_similarity
import pandas as pd
import numpy as np


class Duplication:
    """
    Find duplicates values in a Dataframe by using the function detect_duplicates

    Parameters
    ----------
    var_threshold : variables for the threshold comparing
    var_similarity : variables for the similarity comparing
    variable_testing : variable for find duplicates
    df_pcr : dataframe of pcr test 
    confidence : threshold similarity for the similarity between two values
    threshold : pourcentage of identical values to compute a observation to duplicate
    metric : function to compare string (default is Jaro Winkler similarity)
    """
    
    def __init__(self, var_threshold: list,
                 var_similarity: list,
                 variable_testing: list,
                 df_pcr: pd.DataFrame,
                 confidence=0.9, threshold=0.7,
                 metric=None, remove_dupli_pi=True):

        self.var_threshold = var_threshold
        self.var_similarity = var_similarity
        self.confidence = confidence
        self.threshold = threshold
        self.variable_testing = variable_testing
        self.df_pcr = df_pcr
        self.remove_dupli_pi = remove_dupli_pi  
        
        if metric == None:
            self.metric = jaro_winkler_similarity
        else :
            self.metric = metric


    def detect_duplicates(self, df_patient):
        """
        Find all duplicates in a pandas dataframe for each variable testing and 
        displays the number of duplicates removed.

        Return
        ------
        df_patient ; dataframe with duplicates removed.

        """

        df_patient_init = df_patient.copy()


        # get all unique values duplicated by a variable
        for variable in self.variable_testing:
            all_unique = df_patient[variable][df_patient[variable].duplicated(
                False)].unique()

            # get index duplicated
            list_dupli = self.__get_indice_duplicated__(
                df_patient, self.df_pcr, variable, all_unique)
            
            # remove duplicates values from an input dataframe 
            df_patient = self.__df_deduplicate__(df_patient, list_dupli, variable)

        # remove id duplicated
        if self.remove_dupli_pi:
            index_dupli_pi = df_patient[df_patient.patient_id.duplicated(False)].index
            df_patient = self.__df_deduplicate__(df_patient, index_dupli_pi, 'patient_id')

        # attribute that shows the number of data removed
        self.removed = round(
            1 - (df_patient.shape[0] / df_patient_init.shape[0]), 2)

        return df_patient

    def __get_indice_duplicated__(self, df_patient, df_pcr, variable, all_dupli):
        """
        Find index duplicated values.

        Parameters
        ----------

        df_patient : dataframe, dataset patient
        df_pcr : dataframe, dataset pcr
        variable : str, reference variable to retain duplicates
        all_dupli : list, all uniques values 
        """
        indice_duplicates = []

        for dupli in all_dupli:

            # create a cluster of duplicates observations according to 
            # the test variable and return the index of the reference 
            # observation used for the comparison
            clus, ref = self.__make_cluster__(
                variable, df_patient, df_pcr, dupli)

            # calculates for each observation of the cluster the pourcentage of matching 
            # with the reference observation
            
            match = self.__matching_cluster__(clus, ref, self.var_similarity)
            

            # sets a threshold to qualify an observation as duplicate and 
            # retains those that do not exceed this threshold
            
            cm = self.__calculate_matching__(match, self.var_threshold)
            duplicate = cm >= self.threshold
            
            if any(duplicate):
                indice_duplicates.extend(duplicate.index[duplicate])

        return indice_duplicates

    def __make_cluster__(self, variable, df_patient, df_pcr, dupli):
        """
        Create a duplicate observation cluster according to a test variable.

        Parameters 
        ----------

        df_patient : dataframe, dataset patient
        df_pcr : dataframe, dataset pcr
        variable : str, reference variable to retain duplicates
        dupli : str or float, one unique value from the list_dupli

        Return 
        ------

        cluster : dataframe of duplicates
        ref_index : int, index of the reference observation
        """

        cluster = df_patient[df_patient[variable] == dupli]

        # Find all observations of the cluster that have been tested in the table pcr
        
        is_tested = cluster.patient_id.isin(df_pcr.patient_id)
        
        # - if one observation is tested : use it as a baseline observation, else
        # choose the first observation
        # - if two or more observations are tested : find out if one of the 
        # patient are postive. Retains the index of the first positive patient, 
        # if there is one. Else, retains the first observation.
        
        if any(is_tested):
            index_tested = is_tested.index[is_tested]
            h_many_id = len(index_tested)

            if h_many_id == 1:
                ref_index = index_tested[0]
            else:
                is_positive = self.__find_positive__(index_tested, df_pcr, df_patient)
                if any(is_positive):
                    index_positive = self.__get_positive__(df_patient, df_pcr, is_positive)
                    ref_index = index_positive[np.isin(index_positive, index_tested)][0]
                else:
                    ref_index = index_tested[0]
        else:
            ref_index = is_tested.index[0]

        return cluster, ref_index

    def __matching_cluster__(self, cluster, ref_index, var_similarity):
        """
        Calculates for each observation of the cluster the pourcentage of matching 
        with the reference observation.

        Parameters
        ----------
        cluster : cluster : dataframe of duplicates
        ref_index : ref_index : int, index of the reference observation
        var_similarity : float, threshold to qualify an observation as duplicate

        Return
        ------
        dataframe : return a boolean dataframe  

        """
        matching = list()

        for line in cluster.index:
            if not(line == ref_index):

                var_identical = {}
                
                # For each of columns of each row (excluding the reference 
                # index) calculates the similarity between two strings with an 
                # algorithm (class parameter) for the chosen variables between referent
                # observation. Else, only compare this values.

                for var in cluster.columns:
                    var_identical["index"] = line

                    if var in var_similarity:
                        var_identical[var] = self.metric(cluster.loc[line, var],
                                                    cluster.loc[ref_index, var]) > self.confidence
                    else:
                        var_identical[var] = cluster.loc[line, var] == cluster.loc[
                        ref_index, var]

                matching.append(var_identical)

        dataframe = pd.DataFrame(matching).set_index('index')
        dataframe.index.name = None
        return dataframe

    def __calculate_matching__(self, match, var_threshold):
        """
        Calcule the pourcentage of matching for each observation in cluster 
        with choosen variables.
        """
        return match[var_threshold].sum(axis=1) / len(var_threshold)

    def __df_deduplicate__(self, df_patient, indice_duplicates, variable):
        """
        Remove duplicates of a pandas dataframe with the indices duplicated.
        """
        list_d = np.array(indice_duplicates)
        print(f"{variable} : {len(indice_duplicates)} lines removed")
        return df_patient.loc[np.setdiff1d(df_patient.index, list_d)]

    def __find_positive__(self, index_tested, df_pcr, df_patient):
        """
        Find if a patient is positive from a pcr dataframe.
        """
        is_positive = df_pcr[df_pcr.patient_id.isin(
            df_patient.loc[index_tested].patient_id)].pcr == "P"
        return is_positive

    def __get_positive__(self, df_patient, df_pcr, is_positive):
        """
        Retains the line of positive patient.
        """
        return df_patient[
        df_patient.patient_id.isin(
            df_pcr.patient_id[is_positive.index[is_positive]])].index


def prepare_patient(df_patient):
    """
    Prepare dataframe patient. This function create :
    localisation, full_address, full_name and born_age.
    """

    df_patient = df_patient.fillna('')
    
    # born and age
    df_patient["born_age"] = df_patient.apply(lambda x: str(
        x["date_of_birth"]).replace('.0', '').replace('nan','') 
    + " " + str(x["age"]).replace('.0','').replace('nan',''), axis=1)
    
    # localisation (postcode, suburb and state)
    df_patient.street_number = df_patient.street_number.replace(
        {"": 0}).astype(int).astype(str).replace({"0": ""})
    df_patient["localisation"] = df_patient.apply(lambda x :
                     x["postcode"] + " " + x["state"] + " " 
                     + x["suburb"], axis=1)
    # full address (number and adress)
    df_patient["full_address"] = df_patient.apply(lambda x : x["street_number"] + " " 
                                                  + x["address_1"], axis=1)
    # full name (surname and given name)
    df_patient["full_name"] = df_patient["surname"] + " " + df_patient["given_name"]
    
    return df_patient


def prepare_pcr(df_pcr, positive_pi, not_dupli_pcr):
    """
    Deduplicate pcr table
    """
    keep = pd.concat([positive_pi, not_dupli_pcr])
    df_pcr = df_pcr.drop_duplicates(keep=False, subset=["patient_id"])
    df_pcr = pd.concat([df_pcr, keep])
    return df_pcr

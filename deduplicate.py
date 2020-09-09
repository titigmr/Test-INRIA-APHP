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
        df_patient_init = df_patient.copy()

        for variable in self.variable_testing:
            all_unique = df_patient[variable][df_patient[variable].duplicated(
                False)].unique()

            list_dupli = self.__get_indice_duplicated__(
                df_patient, self.df_pcr, variable, all_unique)
            
            df_patient = self.__df_deduplicate__(df_patient, list_dupli, variable)

        if self.remove_dupli_pi:
            index_dupli_pi = df_patient[df_patient.patient_id.duplicated(False)].index
            df_patient = self.__df_deduplicate__(df_patient, index_dupli_pi, 'patient_id')

        self.removed = round(
            1 - (df_patient.shape[0] / df_patient_init.shape[0]), 2)

        return df_patient

    def __get_indice_duplicated__(self, df_patient, df_pcr, variable, all_dupli):
        indice_duplicates = []

        for dupli in all_dupli:
            all_cluster = {}
            all_cluster["clus"], all_cluster["ref"] = self.__make_cluster__(
                variable, df_patient, df_pcr, dupli)

            match = self.__matching_cluster__(
                all_cluster["clus"], all_cluster["ref"], self.var_similarity)
            
            cm = self.__calculate_matching__(match, self.var_threshold)

            duplicate = cm >= self.threshold
            
            if any(duplicate):
                indice_duplicates.extend(duplicate.index)

        return indice_duplicates

    def __make_cluster__(self, variable, df_patient, df_pcr, dupli):

        cluster = df_patient[df_patient[variable] == dupli]
        is_tested = cluster.patient_id.isin(df_pcr.patient_id)
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
        matching = list()

        for line in cluster.index:
            if not(line == ref_index):
                var_identical = {}
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
        return match[var_threshold].sum(axis=1) / len(var_threshold)

    def __df_deduplicate__(self, df_patient, indice_duplicates, variable):
        list_d = np.array(indice_duplicates)
        print(f"{variable} : {len(indice_duplicates)} lines removed")
        return df_patient.loc[np.setdiff1d(df_patient.index, list_d)]

    def __find_positive__(self, index_tested, df_pcr, df_patient):
        is_positive = df_pcr[df_pcr.patient_id.isin(
            df_patient.loc[index_tested].patient_id)].pcr == "P"
        return is_positive

    def __get_positive__(self, df_patient, df_pcr, is_positive):
        return df_patient[
        df_patient.patient_id.isin(
            df_pcr.patient_id[is_positive.index[is_positive]])].index


def prepare_df(df_patient):
    """
    Prepare variables of the dataset for the deduplicate function 
    (localisation, full_address, full_name and born_age variables).

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

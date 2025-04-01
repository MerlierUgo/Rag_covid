
from Preprocessing.function import *
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')


class Preprocessing():

    def __init__(self,risk_factor):

        self.stop_words = set(stopwords.words('english')).union(set(stopwords.words('french')))

        self.data_1 = pd.read_csv(risk_factor + "Age.csv")
        self.data_2 = pd.read_csv(risk_factor + "Diabetes.csv")
        self.data_3 = pd.read_csv(risk_factor + "Overweight or obese.csv")


    def start_prepro(self, save_folder, save = True):
        # Renommer les colonnes pour les rendre plus faciles à utiliser
        self.data_1.columns = self.data_1.columns.str.strip().str.lower().str.replace(" ", "_")
        self.data_2.columns = self.data_2.columns.str.strip().str.lower().str.replace(" ", "_")
        self.data_3.columns = self.data_3.columns.str.strip().str.lower().str.replace(" ", "_")


        data_1_processed = process_dataframe(self.data_1,self.stop_words, use_abstract=True)
        data_2_processed = process_dataframe(self.data_2,self.stop_words, use_abstract=True)
        data_3_processed = process_dataframe(self.data_3,self.stop_words, use_abstract=True)

        
        data_1_processed = data_1_processed[["date", "study", "study_link", "journal", "severe", "severe_lower_bound", "severe_upper_bound", "severe_p-value", "severe_significant", "fatality", "fatality_lower_bound", "fatality_upper_bound","fatality_p-value","fatality_significant", "fatality_adjusted", "fatality_calculated", "multivariate_adjustment", "study_type", "sample_size", "study_population", "critical_only", "discharged_vs._death?",'key_word']]
        data_2_processed = data_2_processed[["date", "study", "study_link", "journal", "severe", "severe_lower_bound", "severe_upper_bound", "severe_p-value", "severe_significant", "fatality", "fatality_lower_bound", "fatality_upper_bound","fatality_p-value","fatality_significant", "fatality_adjusted", "fatality_calculated", "multivariate_adjustment", "study_type", "sample_size", "study_population", "critical_only", "discharged_vs._death?",'key_word']]
        data_3_processed = data_3_processed[["date", "study", "study_link", "journal", "severe", "severe_lower_bound", "severe_upper_bound", "severe_p-value", "severe_significant", "fatality", "fatality_lower_bound", "fatality_upper_bound","fatality_p-value","fatality_significant", "fatality_adjusted", "fatality_calculated", "multivariate_adjustment", "study_type", "sample_size", "study_population", "critical_only", "discharged_vs._death?",'key_word']]

        # Application à tes datasets
        data_1_processed = add_numeric_bounds_columns(data_1_processed)
        data_2_processed = add_numeric_bounds_columns(data_2_processed)
        data_3_processed = add_numeric_bounds_columns(data_3_processed)


        add_context(data_1_processed,data_2_processed,data_3_processed)

        # Remplacer les valeurs manquantes par des chaînes vides et convertir en type str
        data_1_processed['context'] = data_1_processed['context'].fillna('').astype(str)
        data_2_processed['context'] = data_2_processed['context'].fillna('').astype(str)
        data_3_processed['context'] = data_3_processed['context'].fillna('').astype(str)


        if save:

            
            data_1_processed.to_csv(save_folder +"Age_Preprocessing.csv", index=False)

            data_2_processed.to_csv(save_folder +"Diabetes_Preprocessing.csv", index=False)

            data_3_processed.to_csv(save_folder +"Overweight_or_obese_Preprocessing.csv", index=False)





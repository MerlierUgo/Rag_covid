import pandas as pd
import plotly.express as px
import re
import plotly.graph_objects as go
from Analyse.function import *

class Analyse():

    def __init__(self, risk_factor):
        df_Age = pd.read_csv(risk_factor + "/Age.csv")
        df_Diabetes = pd.read_csv(risk_factor + "/Diabetes.csv")
        df_overweight = pd.read_csv(risk_factor + "/Overweight or obese.csv")

        self.datasets = {
            'Age Data': df_Age,
            'Diabetes Data': df_Diabetes,
            'Overweight Data': df_overweight
        }

    def affichage_statistiques(self,distribution = True, sample_size = True,proportion = True ):
        
        for name, dataset in self.datasets.items():
            dataset_temp = dataset.copy()
            rename_columns(dataset_temp)
            dataset_temp = extract_sample_studies(dataset_temp)
            dataset_temp["Severe_number"] = dataset_temp["Severe"].astype(str).apply(lambda x: float(re.search(r"\d+(\.\d+)?", x).group()) if re.search(r"\d+(\.\d+)?", x) else None)
            dataset_temp["Fatality_number"] = dataset_temp["Fatality"].astype(str).apply(lambda x: float(re.search(r"\d+(\.\d+)?", x).group()) if re.search(r"\d+(\.\d+)?", x) else None)
            if distribution:
                severe_Fatality_plot_districution(dataset_temp,name)
            if sample_size:
                sample_size_plot_distribution(dataset_temp,name)
            if proportion :
                proportion_presence(dataset_temp,name)
                proportion_significant(dataset_temp,name)












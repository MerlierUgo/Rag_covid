import pandas as pd
import plotly.express as px
import re
import plotly.graph_objects as go

# affichage des distribution avec la p value
def severe_Fatality_plot_districution(dataset, name):

    df_analyse_Severe = dataset.dropna(subset=["Severe_number", "Severe_p-value"]).copy()
    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=df_analyse_Severe["Severe_number"], 
        name="Sévérité", 
        opacity=0.6
    ))

    fig.add_trace(go.Histogram(
        x=df_analyse_Severe["Severe_p-value"], 
        name="p-value Sévérité", 
        opacity=0.6,
        marker_color="red"
    ))
    # ajout d'une ligne à p = 0.05
    fig.add_shape(
        type="line",
        x0=0.05, x1=0.05,
        y0=0, y1=1,
        yref="paper",
        line=dict(color="black", width=2, dash="dash")
    )

    # ajout d'un texte à p = 0.05
    fig.add_annotation(
        x=0.17,  
        y=0.9,  
        yref="paper",
        text="Seuil de signification (p = 0.05)",
        showarrow=False,
        font=dict(color="black", size=12)
    )

    fig.update_layout(
        title=f"Distribution de la Sévérité et de la p-value pour {name}",
        xaxis_title="Valeurs",
        yaxis_title="Fréquence",
        barmode="overlay",  
    )

    fig.show()

    df_analyse_Fatality = dataset.dropna(subset=["Fatality_number", "Fatality_p-value"]).copy()

    fig = go.Figure()

    fig.add_trace(go.Histogram(
        x=df_analyse_Fatality["Fatality_number"], 
        name="Létalité", 
        opacity=0.6
    ))
    # ajout d'une ligne à p = 0.05
    fig.add_shape(
        type="line",
        x0=0.05, x1=0.05,
        y0=0, y1=1,
        yref="paper",  
        line=dict(color="black", width=2, dash="dash")
    )
    # ajout d'un texte à p = 0.05
    fig.add_annotation(
        x=0.17,  
        y=0.9,  
        yref="paper",
        text="Seuil de signification (p = 0.05)",
        showarrow=False,
        font=dict(color="black", size=12)
    )

    fig.add_trace(go.Histogram(
        x=df_analyse_Fatality["Fatality_p-value"], 
        name="p-value Létalité", 
        opacity=0.6,
        marker_color="red"
    ))

    fig.update_layout(
        title=f"Distribution de la Létalité et de la p-value pour {name}",
        xaxis_title="Valeurs",
        yaxis_title="Fréquence",
        barmode="overlay", 
    )

    fig.show()


# distribution du nombre de personne par étude
def sample_size_plot_distribution(dataset,name):
    df_analyse_sample_size = dataset.dropna(subset=["Sample_Size"]).copy()
    fig_sample = px.box(df_analyse_sample_size, y="Sample_Size", title=f"Distribution de la Taille de l'Échantillon pour {name}", 
                         color_discrete_sequence=["green"])
    fig_sample.show()


def rename_columns(dataset):
    dataset.columns = [col.replace(" ", "_") for col in dataset.columns]

# proportion de l'evocation de la gravité et de la létalité de nos revues scientifiques
def proportion_presence(dataset,name):

    nan_count = dataset["Severe"].isna().sum()
    non_nan_count = dataset["Severe"].notna().sum()

    nan_data = pd.DataFrame({
        "Type": ["NaN", "Non NaN"],
        "Count": [nan_count, non_nan_count]
    })
    
    fig = px.pie(nan_data, names="Type", values="Count", title=f"Proportion de NaN dans Severe pour {name}")
    fig.show()


    nan_count = dataset["Fatality"].isna().sum()
    non_nan_count = dataset["Fatality"].notna().sum()

    nan_data = pd.DataFrame({
        "Type": ["NaN", "Non NaN"],
        "Count": [nan_count, non_nan_count]
    })

    fig = px.pie(nan_data, names="Type", values="Count", title=f"Proportion de NaN dans Fatality pour {name}")
    fig.show()



# proportions d'evocation d'impacte significatif dans les revues
def proportion_significant(dataset,name):
    significant = dataset[dataset["Severe_Significant"] == "Significant"]["Severe_Significant"].count()
    non_significant = dataset[dataset["Severe_Significant"] != "Significant"]["Severe_Significant"].count()

    signi_data = pd.DataFrame({
        "Type": ["significant", "non_significant"],
        "Count": [significant, non_significant]
    })

    fig = px.pie(signi_data, names="Type", values="Count", 
             title=f"Proportion de Significant et Non-Significant pour {name}",
             color="Type",
             color_discrete_map={"significant": "royalblue", "non_significant": "lightgray"})
    fig.show()


    significant = dataset[dataset["Fatality_Significant"] == "Significant"]["Fatality_Significant"].count()
    non_significant = dataset[dataset["Fatality_Significant"] != "Significant"]["Fatality_Significant"].count()

    signi_data = pd.DataFrame({
        "Type": ["significant", "non_significant"],
        "Count": [significant, non_significant]
    })

    fig = px.pie(signi_data, names="Type", values="Count", 
             title=f"Proportion de Significant et Non-Significant Léthale pour {name}",
             color="Type",
             color_discrete_map={"significant": "royalblue", "non_significant": "lightgray"})
    fig.show()



# preprocessing pour séparer les études des patients
def extract_sample_studies(dataset):
    def extract_values(sample_str):
        if isinstance(sample_str, str):
            sample_str = sample_str.replace(",", "")

            numbers = re.findall(r"\d+", sample_str)
            
            if len(numbers) == 2: 
                return int(numbers[1]), int(numbers[0])
            elif len(numbers) == 1:  
                return int(numbers[0]), 0

        return None, 0  


    dataset[["Sample_Size", "Studies"]] = dataset["Sample_Size"].apply(lambda x: pd.Series(extract_values(x)))

    return dataset
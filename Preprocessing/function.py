# Import of libraries

import re
import unicodedata
import itertools

import pandas as pd
import numpy as np
import pandas

# Data visualization
import seaborn as sns
import matplotlib.pylab as pl
import matplotlib as m
import matplotlib as mpl
import matplotlib.pyplot as plt
import plotly.express as px
from matplotlib import pyplot as plt



import requests
import io
import PyPDF2
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def get_html_text(url):
    """
    Récupère le contenu texte d'une page web à partir de son URL.
    Exclut les balises script et style.
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            # Supprime les balises script et style
            for element in soup(["script", "style"]):
                element.extract()
            # Récupère le texte brut
            text = soup.get_text(separator=" ")
            return text
        else:
            print(f"Erreur lors du téléchargement de la page: {url} - Code {response.status_code}")
            return ""
    except Exception as e:
        print(f"Exception lors de la lecture de la page {url}: {e}")
        return ""
    


def get_pdf_link(url):
    """
    Si l'URL ne se termine pas par .pdf, télécharge la page HTML et recherche
    le lien PDF en cherchant dans les balises <a> un href contenant 'pdf'.
    Retourne l'URL du PDF ou None s'il n'est pas trouvé.
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"Erreur lors du téléchargement de la page: {url} - Code {response.status_code}")
            return None
        soup = BeautifulSoup(response.text, 'html.parser')
        pdf_link = None
        # Recherche d'un lien contenant 'pdf' dans le href
        for a in soup.find_all('a', href=True):
            href = a['href']
            if 'pdf' in href.lower():
                pdf_link = urljoin(url, href)
                break
        if pdf_link is None:
            print(f"Aucun lien PDF trouvé sur la page: {url}")
        return pdf_link
    except Exception as e:
        print(f"Exception lors de l'extraction du lien PDF pour {url}: {e}")
        return None




def download_pdf(url):
    """
    Télécharge le contenu du PDF depuis l'URL.
    Retourne le contenu binaire du PDF ou None en cas d'erreur.
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.content
        else:
            print(f"Erreur lors du téléchargement: {url} - Code {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception pour {url}: {e}")
        return None



def extract_text_from_pdf(pdf_content):
    """
    Extrait le texte d'un PDF à partir de son contenu binaire.
    Essaie d'abord avec PyPDF2 et, en cas d'erreur, utilise pdfminer.six.
    """
    text = ""
    try:
        pdf_file = io.BytesIO(pdf_content)
        reader = PyPDF2.PdfReader(pdf_file)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
    except Exception as e:
        print(f"Erreur d'extraction du texte avec PyPDF2: {e}")
        # Revenir au début du fichier
        pdf_file.seek(0)
        try:
            from pdfminer.high_level import extract_text
            text = extract_text(pdf_file)
        except Exception as e2:
            print(f"Erreur d'extraction du texte avec pdfminer: {e2}")
    return text



def extract_html_section_text(url, container_id=None, container_class=None):
    """
    Récupère le texte d'une zone précise (spécifiée par 'container_id' ou 'container_class')
    dans une page HTML. Si la zone n'est pas trouvée, renvoie le texte du <body>.
    Supprime les balises <script> et <style> avant de renvoyer le texte brut.
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"Erreur lors de la requête: {url} - Code {response.status_code}")
            return ""
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # On tente de récupérer le container spécifié (priorité à l'id, sinon la classe)
        container = None
        if container_id:
            container = soup.find(id=container_id)
        elif container_class:
            container = soup.find(class_=container_class)
        
        # Si on ne trouve pas la zone ciblée, on récupère tout le body
        if not container:
            container = soup.find('body')
            if not container:
                return ""
        
        # Supprime les scripts et styles
        for element in container(["script", "style"]):
            element.extract()
        
        # Récupère le texte brut
        text = container.get_text(separator=" ")
        return text.strip()
    
    except Exception as e:
        print(f"Exception lors de l'extraction du texte depuis {url}: {e}")
        return ""








def extract_keywords(text,stop_words, top_n=5):
    """
    Extrait les 'top_n' mots-clés du texte en se basant sur la fréquence des mots.
    """
    # Mise en minuscules et suppression de la ponctuation
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    tokens = word_tokenize(text)
    
    # Retirer les stop words et les tokens non alphabétiques
    filtered_tokens = [token for token in tokens if token.isalpha() and token not in stop_words]
    
    # Calcul de la fréquence
    freq = {}
    for token in filtered_tokens:
        freq[token] = freq.get(token, 0) + 1
    
    # Tri par fréquence décroissante
    sorted_tokens = sorted(freq.items(), key=lambda x: x[1], reverse=True)
    # Sélection des top_n mots-clés
    keywords = [token for token, count in sorted_tokens[:top_n]]
    return keywords



def process_dataframe(df, stop_words, use_abstract=False):
    """
    Pour chaque ligne du DataFrame, vérifie si l'URL dans "study_link" pointe directement vers un PDF.
    Sinon, tente d'extraire le lien PDF depuis la page HTML.
    Si aucun PDF n'est trouvé, récupère le texte de la page HTML ou de la section 'abstract'
    pour en déduire 5 mots-clés (en fonction de 'use_abstract').
    Ajoute une colonne 'key_word' au DataFrame.
    """
    keywords_list = []
    for index, row in df.iterrows():
        study_url = row['study_link']
        print(f"Traitement de l'article {index} : {study_url}")
        
        # 1) Vérifie si l'URL se termine par .pdf, sinon essaie de récupérer le lien PDF
        if not study_url.lower().endswith('.pdf'):
            pdf_url = get_pdf_link(study_url)
            if pdf_url:
                # Correction pour retirer le suffixe '+html' s'il existe
                if '+html' in pdf_url:
                    pdf_url = pdf_url.replace('+html', '')
                print(f"Lien PDF trouvé: {pdf_url}")
            else:
                print("Aucun lien PDF trouvé, on va extraire le texte HTML.")
                
                # 2) Soit on cible spécifiquement l'abstract (si use_abstract=True),
                #    soit on prend tout le HTML.
                if use_abstract:
                    html_text = extract_html_section_text(study_url, container_id="eng-abstract")
                    if not html_text:  # Si pas trouvé, on essaie tout le body
                        html_text = get_html_text(study_url)
                else:
                    html_text = get_html_text(study_url)
                
                # Extraction de mots-clés
                if html_text:
                    keywords = extract_keywords(html_text,stop_words, top_n=5)
                else:
                    keywords = []
                
                keywords_list.append(keywords)
                continue
        else:
            pdf_url = study_url

        # 3) Lecture du PDF depuis le web
        try:
            response = requests.get(pdf_url, timeout=10)
            if response.status_code == 200:
                pdf_content = response.content
            else:
                print(f"Erreur lors de la lecture du PDF: {pdf_url} - Code {response.status_code}")
                # En cas d'erreur, fallback sur le HTML
                if use_abstract:
                    html_text = extract_html_section_text(study_url, container_id="eng-abstract")
                    if not html_text:
                        html_text = get_html_text(study_url)
                else:
                    html_text = get_html_text(study_url)
                
                if html_text:
                    keywords = extract_keywords(html_text,stop_words, top_n=5)
                else:
                    keywords = []
                keywords_list.append(keywords)
                continue
        except Exception as e:
            print(f"Exception lors de la lecture du PDF: {pdf_url}: {e}")
            if use_abstract:
                html_text = extract_html_section_text(study_url, container_id="eng-abstract")
                if not html_text:
                    html_text = get_html_text(study_url)
            else:
                html_text = get_html_text(study_url)
            
            if html_text:
                keywords = extract_keywords(html_text,stop_words, top_n=5)
            else:
                keywords = []
            keywords_list.append(keywords)
            continue
        
        # 4) Extraction du texte depuis le PDF
        text = extract_text_from_pdf(pdf_content)
        if text:
            keywords = extract_keywords(text,stop_words, top_n=5)
        else:
            # Si le PDF est vide ou inexploitable, fallback HTML
            if use_abstract:
                html_text = extract_html_section_text(study_url, container_id="eng-abstract")
                if not html_text:
                    html_text = get_html_text(study_url)
            else:
                html_text = get_html_text(study_url)
            if html_text:
                keywords = extract_keywords(html_text,stop_words, top_n=5)
            else:
                keywords = []
        
        keywords_list.append(keywords)
    
    df['key_word'] = keywords_list
    return df

# Fonction pour ajouter les colonnes numériques et de vérification des bornes
def add_numeric_bounds_columns(dataset):
    dataset["Severe_number"] = dataset["severe"].astype(str).apply(
        lambda x: float(re.search(r"\d+(\.\d+)?", x).group()) if re.search(r"\d+(\.\d+)?", x) else None
    )
    dataset["Fatality_number"] = dataset["fatality"].astype(str).apply(
        lambda x: float(re.search(r"\d+(\.\d+)?", x).group()) if re.search(r"\d+(\.\d+)?", x) else None
    )
    dataset["severe_outside_bounds"] = (
        (dataset["Severe_number"] < dataset["severe_lower_bound"]) |
        (dataset["Severe_number"] > dataset["severe_upper_bound"])
    ).astype(int)
    dataset["fatality_outside_bounds"] = (
        (dataset["Fatality_number"] < dataset["fatality_lower_bound"]) |
        (dataset["Fatality_number"] > dataset["fatality_upper_bound"])
    ).astype(int)
    return dataset






def add_context(data_1_processed,data_2_processed,data_3_processed):

        # Création d'une colonne 'context' dans data_1_processed, data_2_processed ,data_3_processed
    # Cette colonne regroupe plusieurs informations clés de l'étude sous forme de texte lisible.
    data_1_processed["context"] = (
        "Date: " + data_1_processed["date"].astype(str) + ". " +
        "Study: " + data_1_processed["study"] + ". " +
        "Study Link: " + data_1_processed["study_link"] + ". " +
        "Journal: " + data_1_processed["journal"] + ". " +
        "Severe: " + data_1_processed["severe"].astype(str) + ". " +
        "Severe Lower Bound: " + data_1_processed["severe_lower_bound"].astype(str) + ". " +
        "Severe Upper Bound: " + data_1_processed["severe_upper_bound"].astype(str) + ". " +
        "Severe p-value: " + data_1_processed["severe_p-value"].astype(str) + ". " +
        "Severe Significant: " + data_1_processed["severe_significant"].astype(str) + ". " +
        "Fatalyty : "+ data_1_processed["fatality"].astype(str) + ". " +
        "Fatality lower bound : "+ data_1_processed["fatality_lower_bound"].astype(str) + ". " +
        "Fatality upper bound: "+ data_1_processed["fatality_upper_bound"].astype(str) + ". " +
        "Fatality p-value: "+ data_1_processed["fatality_p-value"].astype(str) + ". " +
        "Fatality Significant: " + data_1_processed["fatality_significant"].astype(str) + ". " +
        "Fatality Adjusted: " + data_1_processed["fatality_adjusted"].astype(str) + ". " +
        "Fatality Calculated: " + data_1_processed["fatality_calculated"].astype(str) + ". " +
        "Multivariate Adjustment: " + data_1_processed["multivariate_adjustment"].astype(str) + ". " +
        "Study Type: " + data_1_processed["study_type"] + ". " +
        "Sample Size: " + data_1_processed["sample_size"].astype(str) + ". " +
        "Study Population: " + data_1_processed["study_population"] + ". " +
        "Critical Only: " + data_1_processed["critical_only"] + ". " +
        "Discharged vs Death: " + data_1_processed["discharged_vs._death?"] + "." +
        "Severe_number: " + data_1_processed["Severe_number"].astype(str) + ". " +
        "Fatality_number: " + data_1_processed["Fatality_number"].astype(str) + ". " +
        "Severe_outside_bounds: " + data_1_processed["severe_outside_bounds"].astype(str) + ". " +
        "Fatality_outside_bounds: " + data_1_processed["fatality_outside_bounds"].astype(str) + ". " +
        "Key word: " + data_1_processed["key_word"].astype(str) + ". " 
    )


    data_2_processed["context"] = (
        "Date: " + data_2_processed["date"].astype(str) + ". " +
        "Study: " + data_2_processed["study"] + ". " +
        "Study Link: " + data_2_processed["study_link"] + ". " +
        "Journal: " + data_2_processed["journal"] + ". " +
        "Severe: " + data_2_processed["severe"].astype(str) + ". " +
        "Severe Lower Bound: " + data_2_processed["severe_lower_bound"].astype(str) + ". " +
        "Severe Upper Bound: " + data_2_processed["severe_upper_bound"].astype(str) + ". " +
        "Severe p-value: " + data_2_processed["severe_p-value"].astype(str) + ". " +
        "Severe Significant: " + data_2_processed["severe_significant"].astype(str) + ". " +
        "Fatalyty : "+ data_2_processed["fatality"].astype(str) + ". " +
        "Fatality lower bound : "+ data_2_processed["fatality_lower_bound"].astype(str) + ". " +
        "Fatality upper bound: "+ data_2_processed["fatality_upper_bound"].astype(str) + ". " +
        "Fatality p-value: "+ data_2_processed["fatality_p-value"].astype(str) + ". " +
        "Fatality Significant: " + data_2_processed["fatality_significant"].astype(str) + ". " +
        "Fatality Adjusted: " + data_2_processed["fatality_adjusted"].astype(str) + ". " +
        "Fatality Calculated: " + data_2_processed["fatality_calculated"].astype(str) + ". " +
        "Multivariate Adjustment: " + data_2_processed["multivariate_adjustment"].astype(str) + ". " +
        "Study Type: " + data_2_processed["study_type"] + ". " +
        "Sample Size: " + data_2_processed["sample_size"].astype(str) + ". " +
        "Study Population: " + data_2_processed["study_population"] + ". " +
        "Critical Only: " + data_2_processed["critical_only"] + ". " +
        "Discharged vs Death: " + data_2_processed["discharged_vs._death?"] + "." +
        "Severe_number: " + data_2_processed["Severe_number"].astype(str) + ". " +
        "Fatality_number: " + data_2_processed["Fatality_number"].astype(str) + ". " +
        "Severe_outside_bounds: " + data_2_processed["severe_outside_bounds"].astype(str) + ". " +
        "Fatality_outside_bounds: " + data_2_processed["fatality_outside_bounds"].astype(str) + ". " +
        "Key word: " + data_2_processed["key_word"].astype(str) + ". " 
    )
    data_3_processed["context"] = (
        "Date: " + data_3_processed["date"].astype(str) + ". " +
        "Study: " + data_3_processed["study"] + ". " +
        "Study Link: " + data_3_processed["study_link"] + ". " +
        "Journal: " + data_3_processed["journal"] + ". " +
        "Severe: " + data_3_processed["severe"].astype(str) + ". " +
        "Severe Lower Bound: " + data_3_processed["severe_lower_bound"].astype(str) + ". " +
        "Severe Upper Bound: " + data_3_processed["severe_upper_bound"].astype(str) + ". " +
        "Severe p-value: " + data_3_processed["severe_p-value"].astype(str) + ". " +
        "Severe Significant: " + data_3_processed["severe_significant"].astype(str) + ". " +
        "Fatalyty : "+ data_3_processed["fatality"].astype(str) + ". " +
        "Fatality lower bound : "+ data_3_processed["fatality_lower_bound"].astype(str) + ". " +
        "Fatality upper bound: "+ data_3_processed["fatality_upper_bound"].astype(str) + ". " +
        "Fatality p-value: "+ data_3_processed["fatality_p-value"].astype(str) + ". " +
        "Fatality Significant: " + data_3_processed["fatality_significant"].astype(str) + ". " +
        "Fatality Adjusted: " + data_3_processed["fatality_adjusted"].astype(str) + ". " +
        "Fatality Calculated: " + data_3_processed["fatality_calculated"].astype(str) + ". " +
        "Multivariate Adjustment: " + data_3_processed["multivariate_adjustment"].astype(str) + ". " +
        "Study Type: " + data_3_processed["study_type"] + ". " +
        "Sample Size: " + data_3_processed["sample_size"].astype(str) + ". " +
        "Study Population: " + data_3_processed["study_population"] + ". " +
        "Critical Only: " + data_3_processed["critical_only"] + ". " +
        "Discharged vs Death: " + data_3_processed["discharged_vs._death?"] + "." +
        "Severe_number: " + data_3_processed["Severe_number"].astype(str) + ". " +
        "Fatality_number: " + data_3_processed["Fatality_number"].astype(str) + ". " +
        "Severe_outside_bounds: " + data_3_processed["severe_outside_bounds"].astype(str) + ". " +
        "Fatality_outside_bounds: " + data_3_processed["fatality_outside_bounds"].astype(str) + ". " +
        "Key word: " + data_3_processed["key_word"].astype(str) + ". " 
    )


    return data_1_processed,data_2_processed,data_3_processed










































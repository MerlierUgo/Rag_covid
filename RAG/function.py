import pandas as pd

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma


from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA


import tkinter as tk
from tkinter import scrolledtext
from langchain_ollama import OllamaLLM
import os




# Fonction pour segmenter un document en morceaux de 512 tokens
def segmenter_texte(texte, longueur_max=512):
    tokens = texte.split()
    segments = []
    for i in range(0, len(tokens), longueur_max):
        segment = ' '.join(tokens[i:i + longueur_max])
        segments.append(segment)
    return segments





# Fonction pour construire la requête complète en ajoutant l'instruction par défaut
def build_query(user_query):

    default_instruction = ("Tu es un médecin empathique qui sait synthétiser les informations pour que les patients comprennent facilement. Tu as accès à de nombreuses revues scientifiques. Un patient, inquiet à propos de sa maladie actuelle, le COVID-19, te pose une question sur un facteur qu’il pense être ou ne pas être un facteur de risque. Tu dois lui donner une réponse synthétique, basée sur les résumés d’articles scientifiques auxquels tu as accès. Explique-lui simplement si ce facteur représente ou non un risque en termes de gravité du virus ou de sa létalité. N’hésite pas à faire preuve de compréhension et de douceur. Les patients peuvent être stressés et inquiets. Voici le patient.")

    return default_instruction + "\n" + user_query






import pandas as pd
from RAG.function import *


class Rag():

    def __init__(self, path_prepro, llm_name, embedding_model_name):
        self.data_1 = pd.read_csv(path_prepro + '/Age_Preprocessing.csv')
        self.data_2 = pd.read_csv(path_prepro + '/Diabetes_Preprocessing.csv')
        self.data_3 = pd.read_csv(path_prepro + '/Overweight_or_obese_Preprocessing.csv')

        self.combined_data = pd.concat([self.data_1, self.data_2, self.data_3], ignore_index=True)

        # Appliquer la segmentation à chaque document de la colonne 'context'
        documents = self.combined_data['context'].dropna().tolist()
        segmented_docs = []

        for doc in documents:
            segmented_docs.extend(segmenter_texte(doc))

        embedding_model = HuggingFaceEmbeddings(
            model_name=embedding_model_name,
            model_kwargs={'device': 'cpu', 'truncate_dim': 1024}
        )

        persist_dir = "./chroma_static_mrl"
        vectorstore = Chroma.from_texts(segmented_docs, embedding_model, persist_directory=persist_dir)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

        self.llm = Ollama(model=llm_name)
        self.qa_chain = RetrievalQA.from_chain_type(llm=self.llm, retriever=retriever)

    def run_query(self):

        root = tk.Tk()
        root.title("Chat avec LLM")

        output_text = tk.Text(root, wrap=tk.WORD, height=20, width=80)
        output_text.pack(padx=10, pady=10)

        entry = tk.Entry(root, width=80)
        entry.pack(padx=10, pady=(0, 10))

        default_instruction = (
            "Tu es un assistant intelligent qui répond uniquement en te basant sur les documents fournis. "
            "Si tu ne trouves pas la réponse dans les documents, dis simplement : 'Je ne sais pas'. "
            "N'invente jamais d'informations et ne réponds pas en dehors des sources fournies."
            "Tu prendra le rolle d'un docteur empathique et qui sait synthétiser les choses pour que les patients comprennent simplement. "
            "Tu as accès à de nombreuses revues scientifiques. Un patient, ayant peur sur la maladie actuelle, le covid-19, "
            "te pose une question sur un facteur qu'il pense être à risque ou non. Tu dois donc lui répondre en synthèse, "
            "selon les résumés de revues scientifiques que tu possèdes. Tu dois l'expliquer simplement si oui ou non ce "
            "facteur est un risque sur l'atteinte de la gravité du virus ou sur sa létalité. N'hésite pas à être compréhensif "
            "et doux. Les patients peuvent être stressés et inquiets. Voici la question du patient, n'oublie pas de faire une "
            "synthèse de 3-4 phrases maximums."
        )

        chat_history = [{"role": "system", "content": default_instruction}]

        def get_ai_response():
            """Récupère la réponse du modèle et garde l'historique."""
            user_input = entry.get().strip()
            if not user_input:
                output_text.insert(tk.END, "Veuillez entrer un message.\n")
                return

            chat_history.append({"role": "user", "content": user_input})

            # Construire le prompt en excluant l'instruction système de l'affichage
            formatted_prompt = "\n".join(
                [f"{msg['role']}: {msg['content']}" for msg in chat_history if msg["role"] != "system"]
            )

            full_prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in chat_history])
            response = self.qa_chain.run(full_prompt)

            chat_history.append({"role": "assistant", "content": response})

            # Afficher uniquement la conversation sans l'instruction système
            output_text.insert(tk.END, f"Utilisateur : {user_input}\nIA : {response.strip()}\n\n")
            output_text.see(tk.END)  # Fait défiler vers le bas

            entry.delete(0, tk.END)

        send_button = tk.Button(root, text="Envoyer", command=get_ai_response)
        send_button.pack(padx=10, pady=(0, 10))

        entry.bind("<Return>", lambda event: get_ai_response())  # Permet d'envoyer avec la touche Entrée

        root.mainloop()

















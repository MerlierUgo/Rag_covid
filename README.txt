


# COVID-19 Open Research Dataset Challenge


![Exemple de sortie](./assets/front.png)


## Introduction
<p align="justify">
ors de ce rapport, nous allons passer en revue notre deuxième projet d’IA dans le cadre de notre dernière année d’école d’ingénieur à Cy-Tech, option Intelligence Artificielle. Ce projet est à choisir parmi les challenges Kaggle disponibles sur Internet. Durant le premier projet, nous avions décidé de travailler sur les GAN, un type de modèle génératif que nous n’avions pas encore étudié. Aujourd’hui, nous avons choisi comme second projet la création d’un RAG (Retrieval-Augmented Generation), une compétence de plus en plus demandée dans le monde de l’entreprise.

</p>


## Dataset
<p align="justify">
Le challenge Kaggle nous offre les données nécessaires pour la création du RAG. Des tableaux Excel, contenant, pour chaque ligne, les résumés des revues scientifiques, sont triés selon les grands thèmes.Maintenant, il faut choisir les revues scientifiques pour notre RAG. Naturellement, nous nous sommes tournés vers le thème des risques. En effet, selon nous, c’est le genre de question qui serait le plus demandé en cas d’épidémie mondiale.Nous prenons donc le thème 8_risk_factors présent dans les données fournies et nous choisissons trois risques : l’âge, le surpoids ou obésité, et le diabète. Ces trois risques sont, selon nous, assez représentatifs des questions principalement posées dans ce contexte. Regardons ensemble plus en détails notre dataset. Nous avons une colonne \textt{"Severe"} qui nous donne la mesure du risque de développer une forme grave du Covid-19. Si la valeur est plus petite ou égale à 1, alors il n’y a pas de risque. On a également deux colonnes pour nous donner l'intervalle de confiance. En effet, la valeur n’est pas forcément strictement égale à 1 ; alors si l’intervalle n'inclut pas 1, on peut dire que c’est significatif. Cette information est ajoutée à une colonne dédiée : Severe_Significant.
</p>


<p align="center">
  <img src="./assets/age.png" />
</p>

<p align="center">
  Les distribution de la gravit´e de l’ˆage sur la maladie et de la p-value
</p>
<br>


<p align="justify">

On aperçoit sur les graphiques ci-dessus que les 3 facteurs que les p valeur sont majoritairement supérieur à 0.05. On peut donc dire que statistiquement, on a une corrélation peut convaincante. De plus, pour l'âge, les valeurs de gravité sont autour de 1, suggérant un lien peu significatif. Néanmoins, pour le diabète et le surpoids, on a des valeurs bien supérieures à 1 laissant penser à un impact plus fort. Il y aurait donc une certaine nuance entre le diabète et le surpoids face à l'âge. Cela peut nous aider par la suite à ajuster le LLM pour répondre aux questions.
</p>


## Preprocessing


<p align="justify">
Nos 3 datasets sont déjà des résumés de nos études. Nous n’avions pas un gros preprocesing à faire. Néanmoins on a décidé de rajouter une colonne pour sélectionner les mots les plus importants dans le texte pour aider notre LLM. On a donc sélectionné les plus pertinentes notamment par la fréquence d’apparition et on a tokenisé tout ça dans une colonne. Enfin, on a concaténé l’intégralité des colonnes dans une colonne nommée 'Contexte' qui est également tokenisé et qui servira pour nos embeddings. 
</p>


## Embedding
<p align="justify">
Tout d’abord, nous devons modifier nos données d’entrée pour qu’elles soient comprises par notre futur modèle LLM, mais également pour qu’il y accède rapidement. Meilleure sera notre vectorisation des données, meilleures seront les réponses de notre LLM sur ces sujets. En effet, pour que le RAG soit efficace, il faut vectoriser nos résumés, qui seront par la suite comparés avec la question posée, elle aussi vectorisée. Afin de transformer ces résumés en vecteurs, nous avons choisi le modèle static-retrieval-mrl-en-v1. Ce modèle appartient à la famille des Sentence-Transformers, une architecture optimisée pour produire des représentations vectorielles de phrases en haute dimension. Il est spécialement conçu pour la récupération d’informations, permettant d’encoder du texte sous forme de vecteurs denses adaptés à la recherche sémantique.
Dans notre cas, chaque document, et en l’occurrence chaque ligne de notre colonne "contexte", est encodé en vecteur. La requête du prompt est également encodée. On effectue ensuite une recherche de similarité entre le vecteur de la requête et ceux de tous nos documents. C’est pourquoi il est crucial que ces derniers soient bien vectorisés, afin de pouvoir les parcourir rapidement et efficacement. On récupère ainsi les documents les plus pertinents, que l’on transmet au LLM de sortie pour qu’il les exploite dans sa réponse.
</p>


## LLM
<p align="justify">
Le LLM utilisé est llama 3.2. Ce modèle est open source, gratuit, performant et léger en termes de stockage. Pour chaque appel, nous avons un prompt d’initialisation. Ce dernier permet de donner le contexte et d’aiguiller le modèle sur une façon de répondre. Dans notre cas, nous lui avons précisé qu’il était docteur et qu’il devait synthétiser les réponses pour répondre au patient sur les risques potentiels face au virus. On a également précisé qu’il devait être empathique et comprendre la potentielle détresse du patient, cela permet d’avoir un message plus cohérent dans le contexte de pandémie.
</p>
## Resultat
<p align="justify">
Voici quelques exemples de prompts représentant quelqu’un d’inquiet sur sa santé en fonction des 3 facteurs choisis face au virus. On remarque que notre “agent médical” est rassurant et s’inspire des revues qu’on lui a donné. Il évite d’inventer et nous conseille même sur certains points. Comme analysé au début de notre étude, l'âge est bien considéré comme un risque létal selon lui. Néanmoins, il nuance sur le fait que ça peut être couplé à un autre facteur et donc permet de diminuer le stress du patient. De plus, nous avons construit notre RAG pour que l’agent ait de la mémoire. Cela permet une conversation plus fluide et des réponses plus claires. Enfin, l’interface graphique permet à notre utilisateur, ici le patient, un environnement plus agréable et rassurant.
</p>

<p align="center">
  <img src="./assets/resume.png" />
</p>

<p align="center">
  Exemple de prompt
</p>
<br>

## Conclusion
<p align="justify">
Notre RAG est efficace tant dans la forme que dans le fond. Il peut permettre de garder une partie de la population informée face aux médias de désinformations. Pour le mettre à jour, il suffit de rajouter un document dans la pipeline et il sera pris en compte dans l’embedding utilisé par le LLM. C’est un processus facile à améliorer du fait qu’il n’y a pas de réels entraînements dus à l'utilisation d’un LLM déjà entraîné. Néanmoins, pour avoir des interactions de meilleure qualité, on peut envisager un modèle plus demandant en ressource comme GPT 4. De plus, en général, les entreprises ne sont pas favorables à l’utilisation d’un LLM externe dans leur RAG. C’est pourquoi il est possible de changer le modèle par un créé en interne. Ce challenge nous a beaucoup appris sur la manière de fonctionner d’un RAG.
</p>

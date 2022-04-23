from pymongo import MongoClient
import networkx as nx
import pandas as pd
from bokeh.io import output_file, show
from bokeh.models import (BoxZoomTool, Circle, HoverTool, 
                          MultiLine,Plot, Range1d, ResetTool, Column, Div,Row)
from bokeh.palettes import Blues8
from bokeh.plotting import from_networkx, figure
from bokeh.transform import linear_cmap


# Réseau de publications scientifiques

# connection à la base de données
db_uri = "mongodb+srv://etudiant:ur2@clusterm1.0rm7t.mongodb.net/"
client = MongoClient(db_uri)
db = client["publications"]

# sélection de la collection
coll = db["hal_irisa_2021"]

# On regarde les indexes présents dans la base de données
print(coll.index_information())

# Sélection des auteurs avec leurs publications
# La requete ci-dessous est suffisante sur MongoDB mais ne nous permet pas
# une récupération des valeurs dans la variable titre ...
# nous utiliserons la requete 2

# auteurspublications = coll.aggregate([
#                         {"$unwind": "$authors"},
#                         {"$group": {"_id": {"name": "$authors.name",
#                                         "firstname": "$authors.firstname"},
#                                     "titre": {"$push": "$title"},
#                                     "nbpubli": {$sum: 1}}},
#                         {"$sort": {"nbpubli": -1}},
#                         {"$limit": 20}                        
#                         ])  

auteurspublications = coll.aggregate([
                        {"$unwind": "$authors"},
                        {"$group": {"_id": {"name": "$authors.name",
                                        "firstname": "$authors.firstname"},
                                    "titre": {"$push": "$title"},
                                    "nbpubli": {"$sum": 1}}},
                        {"$sort": {"nbpubli": -1}},
                        {"$limit": 20},
                        {"$group": {"_id": {"name": "$_id.name",
                            "firstname": "$_id.firstname",
                            "titre" : "$titre",
                            "nbpubli": "$nbpubli"}}}   
                        ])        

# Récupération dans listes les noms des auteurs, leur prénom et leurs publications
auteurs = [nom["_id"] for nom in auteurspublications]

# Création d'un dataframe avec les noms, prénoms et liste de publications associés à chaque auteurs
#data = pd.DataFrame(auteurs) 
rows = []
for data in auteurs:  
    rows.append(data) 
  
df = pd.DataFrame(rows) 

# Création d'une liste avec le nombre de publications associé à chaque auteur
# Création d'une liste de publication commun entre deux auteurs
# Création d'une liste avec le noeud cible et d'une liste avec le noeud source
nbrepubli = []
nbrepublicommun = []
noeudcible = []
noeudsource = []
for source in df.name:
    publisource = list(df.titre[df.name == source])[0]

    for cible in df.name:
        if cible == source:
            continue
        
        publicible = list(df.titre[df.name == cible])[0]
        
        cmp = {}
        publitotale = publisource + publicible
        
        lstelem =[]
        lstcompte = []
        for elem in publitotale:
            if elem not in lstelem:
                lstelem.append(elem)
                compte = publitotale.count(elem)
                if compte != 1:
                    lstcompte.append(compte)
        commun = len(lstcompte)
        
        # for elem in publitotale:
        #     cmp[elem] = cmp.get(elem,0) + 1

        # commun = 0
        # for nbre in cmp.values():
        #     if nbre != 1:
        #         commun += 1
        
        publitotale = []

        noeudsource.append(source)
        noeudcible.append(cible)
        nbrepublicommun.append(commun)
        nbrepubli.append(int(df.nbpubli[df.name == source]))
        
# dataframe à utiliser pour le network
datagraphbis = pd.DataFrame({"source": noeudsource, "target": noeudcible, "weight": nbrepublicommun, "node_size": nbrepubli})

# sélection des lignes où les individus ont un lien
df_mask=datagraphbis['weight'] > 0
datagraph = datagraphbis[df_mask]


# Transformation du dataframe en reseau
G = nx.from_pandas_edgelist(datagraph)
# visualisation basique
nx.draw(G, with_labels=True,width=datagraph.weight)
nx.draw_circular(G, with_labels=True, width=datagraph.weight)


# Préparation des données
auteurunique = datagraph.copy()
auteurunique.drop_duplicates(subset ="source", keep = 'first', inplace=True)

# Dictionnaire auteur et taille de noeud (nbre de publications)
dico = {}
i=0
for auteur in auteurunique.source:
    dico[auteur] = auteurunique.node_size.values[i]
    i+=1

# Dictionnaire liens et taille du lien (nbre de publications en commun)
i=0
dicoedges = {}
for edge in G.edges():
    dicoedges[edge] = datagraph.weight.values[i]
    i+=1
    
# ajouter le dico créé comme attribut du nœud.
nx.set_node_attributes(G, name='adjusted_node_size', values=dico)

# ajouter le dicoedges créé comme attribut du lien.
nx.set_edge_attributes(G, name='weight', values=dicoedges)
    
# Outils de survol sur les noueds
HOVER_TOOLTIPS = [
        ("Auteur", "@index"),
        ("Nbre de publications", "@adjusted_node_size")
]

# Création du graphique
plot = figure(tooltips = HOVER_TOOLTIPS,
              tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',
              x_range=Range1d(-12.1, 12.1), y_range=Range1d(-12.1, 12.1),title='Réseau des 20 auteurs les plus prolifiques et leurs interactions')

# Création du network
network_graph = from_networkx(G, nx.circular_layout, scale=10, center=(0, 0)) #nx.spring_layout

# Choix de la taille et couleur des noeuds en fonction du nombre de publications de l'auteur
minimum_value_color = min(network_graph.node_renderer.data_source.data['adjusted_node_size'])
maximum_value_color = max(network_graph.node_renderer.data_source.data['adjusted_node_size'])
network_graph.node_renderer.glyph = Circle(size='adjusted_node_size', fill_color=linear_cmap('adjusted_node_size', Blues8, minimum_value_color, maximum_value_color))

# Taille des liens
network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.8, line_width='weight') 

plot.renderers.append(network_graph)

#Ajout de code html
div = Div(text="""
<h1> Réseau de publications scientifiques </h1>
<p> La base publications contient les informations relatives aux publications de scientifiques du laboratoire IRISA 
pour l’année 2021 (extraites du service HAL). 
On a visualisé les liens entre les auteurs de ces publications, en utilisant un code couleur qui permette de distinguer les auteurs par
leurs nombres de publications et en représentant les liens (co-publications) existant entre les auteurs. 
Le nombre d’auteurs présents dans la base étant très grand, on se focalise sur les 20 auteurs les plus prolifiques 
(i.e. qui ont participé à l’écriture du plus grand nombre d’articles) .
Notre requête MongoDB récupére pour chacun de ces auteurs la liste de ses publications 
(la suite du traitement qui consiste à calculer le nombre d’articles commun par paire d’auteurs est réalisée 
 dans le script python). </p>
</br>

<p> Le nombre maximal de publications communes est de 11 et celui minimal est de 1. </p>
</br>

<p> Retour à la page d'accueil : <a href="../sommaire.html">ici</a></p>

""")


layout = Row(Column(div, plot, width=900))
output_file("page2.html")
show(layout)



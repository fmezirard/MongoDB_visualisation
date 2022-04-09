from pymongo import MongoClient
import networkx as nx
import pandas as pd
from bokeh.io import output_file, show
from bokeh.models import (BoxZoomTool, Circle, HoverTool,
                          MultiLine, Plot, Range1d, ResetTool, ColumnDataSource, Column, Div,Row)
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

# On va récupérer les 20 auterurs les plus prolifiques
auteursprolifiques  = coll.aggregate([
                        {"$unwind": "$authors"},
                        {"$group": {"_id": {"name": "$authors.name",
                                        "firstname": "$authors.firstname"},
                                    "nb_articles": {"$sum": 1}}},
                        {"$sort": {"nb_articles": -1}},
                        {"$limit": 20}
                      ])

listeauteurs = [nom["_id"] for nom in auteursprolifiques]

# créer une liste auteurs associé à ses publications
# puis garder juste les auteurs de auteursprolifiques

nomauteurs = []
prenomauteurs = []
for couple in listeauteurs:
    nomauteurs.append(couple["name"])
    prenomauteurs.append(couple["firstname"])

print(nomauteurs)
print(prenomauteurs)

# Sélection des auteurs avec leurs publications
auteurspublications = coll.aggregate([
                        {"$unwind": "$authors"},
                        {"$match":{"authors.name": {"$in" : nomauteurs}, "authors.firstname": {"$in":prenomauteurs}}},
                        {"$group": {"_id": {"name": "$authors.name",
                                        "firstname": "$authors.firstname"},
                                    "essai": {"$push": "$title"}}}
                      ])                    

# Récupération dans listes les noms des auteurs, leur prénom et leurs publications
auteurs = [nom["_id"] for nom in auteurspublications]
nomauteurs = []
prenomauteurs = []
for couple in auteurs:
    nomauteurs.append(couple["name"])
    prenomauteurs.append(couple["firstname"])

publications = [nom["essai"] for nom in auteurspublications]
print(publications)


# Création d'un dataframe avec les noms, prénoms et liste de publications associés à chaque auteurs
data = pd.DataFrame({"nomauteurs": nomauteurs, "prenomauteurs":prenomauteurs,"publications":publications})
print(data)

# Création d'une liste avec le nombre de publications associé à chaque auteur
# Création d'une liste de publication commun entre deux auteurs
# Création d'une liste avec le noeud cible et d'une liste avec le noeud source
nbrepubli = []
nbrepublicommun = []
noeudcible = []
noeudsource = []
for source in data.nomauteurs:
    publisource = list(data.publications[data.nomauteurs == source])[0]

    for cible in data.nomauteurs:
        publicible = list(data.publications[data.nomauteurs == cible])[0]
        
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
        nbrepubli.append(len(publisource))
        
# dataframe à utiliser pour le network
datagraph = pd.DataFrame({"source": noeudsource, "target": noeudcible, "weight": nbrepublicommun, "node_size": nbrepubli})
#datagraph = datagraphinitiale[datagraphinitiale.weight != 0]


# Transformation du fataframe en reseau
G = nx.from_pandas_edgelist(datagraph)
# visualisation basique
# nx.draw(G, with_labels=True, width=datagraph.weight)
# nx.draw_circular(G, with_labels=True, width=datagraph.weight)

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


#Choose attributes from G network to size and color by — setting manual size (e.g. 10) or color (e.g. 'skyblue') also allowed
#size_by_this_attribute = 'adjusted_node_size'
#color_by_this_attribute = 'adjusted_node_size'
#size_by_this_attribute_e = 'weight'

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
network_graph = from_networkx(G, nx.spring_layout, scale=10, center=(0, 0)) # nx.circular_layout

# Choix de la taille et couleur des noeuds en fonction du nombre de publications de l'auteur
minimum_value_color = min(network_graph.node_renderer.data_source.data['adjusted_node_size'])
maximum_value_color = max(network_graph.node_renderer.data_source.data['adjusted_node_size'])
network_graph.node_renderer.glyph = Circle(size='adjusted_node_size', fill_color=linear_cmap('adjusted_node_size', Blues8, minimum_value_color, maximum_value_color))

# Choix de la taille du lien en fonction de publications communes entre auteur
#network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width='weight'*10)

#network_graph.edge_renderer.data_source.data["line_width"] = [G.get_edge_data(a,b)['weight'] for a, b in G.edges()]
#network_graph.edge_renderer.glyph.line_width = {'field': 'line_width'}


plot.renderers.append(network_graph)


#Ajout de code html
div = Div(text="""
<h1> Réseau de publications scientifiques </h1>
<p> La base publications contient les informations relatives aux publications de scientifiques du laboratoire IRISA 
pour l’année 2021 (extraites du service HAL). Visualisez les liens entre les auteurs de ces publications, 
en utilisant un code couleur qui permette de distinguer les auteurs par leurs nombres de publications et 
en représentant les liens (co-publications) existant entre les auteurs. 
Le nombre d’auteurs présents dans la base étant très grand, vous vous focaliserez sur les 20 auteurs les plus prolifiques 
(i.e. qui ont participé à l’écriture du plus grand nombre d’articles) 
et votre requête MongoDB devra récupérer pour chacun de ces auteurs la liste de ses publications 
(la suite du traitement qui consiste à calculer le nombre d’articles commun par paire d’auteurs pourra être réalisée 
 dans votre script). </p>
</br>

<p> Retour à la page d'accueil : <a href="../sommaire.html">ici</a></p>

""")


layout = Column(div, plot)
output_file("page2.html")
show(layout)













# #Choose a title!
# title = 'Réseau des 20 auteurs les plus prolifiques et leurs interactions'

# #Establish which categories will appear when hovering over each node
# HOVER_TOOLTIPS = [("Auteur", "@index")]

# #Create a plot — set dimensions, toolbar, and title
# plot = figure(tooltips = HOVER_TOOLTIPS,
#               tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',
#             x_range=Range1d(-10.1, 10.1), y_range=Range1d(-10.1, 10.1), title=title)

# #Create a network graph object with spring layout
# # https://networkx.github.io/documentation/networkx-1.9/reference/generated/networkx.drawing.layout.spring_layout.html
# network_graph = from_networkx(G, nx.spring_layout, scale=10, center=(0, 0))

# #Set node size and color
# network_graph.node_renderer.glyph = Circle(size=15, fill_color='skyblue')

# #Set edge opacity and width
# network_graph.edge_renderer.glyph = MultiLine(line_alpha=0.5, line_width=1)

# #Add network graph to the plot
# plot.renderers.append(network_graph)

# show(plot)
# #save(plot, filename=f"{title}.html")











# code MongoDB
# db.getCollection('hal_irisa_2021').find({"authors.name": {$in : ["Kaim","Canard"]}, 
# "authors.firstname": {$in:["Guillaume","Sébastien"]}})

# code MongoDB
# Récupération des 20 auteurs
#db.getCollection('hal_irisa_2021').aggregate([
 #                       {$unwind: "$authors"},
  #                      {$group: {_id: {name: "$authors.name",
   #                                     firstname: "$authors.firstname"},
    #                                nb_articles: {$sum: 1}}},
     #                               {$sort: {"nb_articles": -1}},
      #                  {$limit: 20}
       #               ])

# db.getCollection('hal_irisa_2021').aggregate([
 #                       {$unwind: "$authors"},
  #                      {$group: {"_id": {"name": "$authors.name",
   #                                     "firstname": "$authors.firstname"},
    #                                "publication": {$push: "$title"}}}
     #                 ])


#db.getCollection('hal_irisa_2021').aggregate([
 #                       {$unwind: "$authors"},
  #                      {$match: {"authors.name":{$in : ['Lefèvre', 'Pacchierotti', 'Pontonnier', 'Lécuyer', 'Fromont', 'Jézéquel', 'Guillemot', 'Busnel', 'Giordano', 'Pettré', 'Maumet', 'Ferré', 'Bannier', 'Legeai', 'Olivier', 'Dumont', 'Rubino', 'Martin', 'Maillé', 'Siegel']}}},                        {$group: {"_id": {"name": "$authors.name",
   #                                     "firstname": "$authors.firstname"},
    #                                "publication": {$push: "$title"}}}])

# Récupération des auteurs + publications
#db.getCollection('hal_irisa_2021').aggregate([
 #                       {$unwind: "$authors"},
  #                      {$match: {"authors.name":{$in : ['Lefèvre', 'Pacchierotti', 'Pontonnier', 'Lécuyer', 
   #                         'Fromont', 'Jézéquel', 'Guillemot', 'Busnel', 'Giordano', 'Pettré', 'Maumet', 'Ferré', 
    #                        'Bannier', 'Legeai', 'Olivier', 'Dumont', 'Rubino', 'Martin', 'Maillé', 'Siegel']},
     #                   "authors.firstname":{$in : ['Sébastien', 'Claudio', 'Charles', 'Elisa', 'Jean-Marc', 'Anatole', 
      #                      'Christine', 'Yann', 'Julien', 'Jean-Christophe', 'Elise', 
       #                     'Georges', 'Anne-Hélène', 'Camille', 'Fabrice', 'PaoloRobuffo', 
        #                    'Arnaud', 'Gerardo', 'Valérie', 'Rémi']}}},                        
         #               {$group: {"_id": {"name": "$authors.name","firstname": "$authors.firstname"},
          #                          "publication": {$push: "$title"}}}])


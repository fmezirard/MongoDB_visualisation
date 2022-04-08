from pymongo import MongoClient
import networkx as nx
import pandas as pd
import numpy as np
from bokeh.io import output_file, show
from bokeh.models import (BoxZoomTool, Circle, HoverTool,
                          MultiLine, Plot, Range1d, ResetTool)
from bokeh.palettes import Spectral4
from bokeh.plotting import from_networkx

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
#print(listeauteurs)


# créer une liste auteurs associé à ses publications
# puis garder juste les auteurs de auteursprolifiques

nomauteurs = []
prenomauteurs = []
for couple in listeauteurs:
    nomauteurs.append(couple["name"])
    prenomauteurs.append(couple["firstname"])

print(nomauteurs)
print(prenomauteurs)


auteurspublications = coll.aggregate([
                        {"$unwind": "$authors"},
                        {"$match":{"authors.name": {"$in" : nomauteurs}, "authors.firstname": {"$in":prenomauteurs}}},
                        {"$group": {"_id": {"name": "$authors.name",
                                        "firstname": "$authors.firstname"},
                                    "publication": {"$push": "$title"}}}
                      ])                    

auteurs = [nom["_id"] for nom in auteurspublications]
nomauteurs = []
prenomauteurs = []
for couple in auteurs:
    nomauteurs.append(couple["name"])
    prenomauteurs.append(couple["firstname"])
#publications = [nom["publication"] for nom in auteurspublications]

publications = []
for publi in auteurspublications:
    publications.append(publi["publication"])

#print(publications)

data = pd.DataFrame({"nomauteurs": nomauteurs, "prenomauteurs":prenomauteurs})#, "publications":publications})
print(data)

nbrepublicommun = []
noeudcible = []
noeudsource = []
for source in data.nomauteurs:
    publisource = data.publications[nomauteurs == source]

    for cible in data.nomauteurs:
        publicible = data.publications[nomauteurs == cible]
        
        cmp = {}
        publitotale = publisource + publicible
        for elem in publitotale:
            cmp["elem"] = cmp.get(elem,0) + 1
        
        commun = 0
        for nbre in cmp.values():
            if nbre != 1:
                commun += 1

    noeudsource.append(source)
    noeudcible.append(cible)
    nbrepublicommun.append(commun)
        

datagraph = pd.DataFrame({"noeudsource": noeudsource, "noeudcible": noeudcible, "nbrepublicommun": nbrepublicommun})

# Préparation pour le graphique 
G = nx.datagraph()

# SAME_PUB, DIFFERENT_PUB = "black", "red"
# edge_attrs = {}

# for start_node, end_node, _ in G.edges(data=True):
#     edge_color = SAME_PUB if G.nodes[start_node]["pub"] == G.nodes[end_node]["pub"] else DIFFERENT_PUB
#     edge_attrs[(start_node, end_node)] = edge_color

# nx.set_edge_attributes(G, edge_attrs, "edge_color")

# Graphique du réseau
plot = Plot(width=400, height=400,
            x_range=Range1d(-1.1, 1.1), y_range=Range1d(-1.1, 1.1))
plot.title.text = "Réseau entre les auteurs"

# Ajout d'un outils de survol, identification du noeud
node_hover_tool = HoverTool(tooltips=[("auteur", "@noeudsource")])
plot.add_tools(node_hover_tool, BoxZoomTool(), ResetTool())

graph_renderer = from_networkx(G, nx.spring_layout, scale=1, center=(0, 0))

graph_renderer.node_renderer.glyph = Circle(size=15, fill_color=Spectral4[0])
graph_renderer.edge_renderer.glyph = MultiLine(line_color="edge_color", line_alpha=0.8, line_width=1)
plot.renderers.append(graph_renderer)

output_file("Page2.html")
show(plot)

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


from pymongo import MongoClient
import networkx as nx
import pandas as pd
import numpy as np

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

for nom in data.nomauteurs:
    publinom = data.publications[nomauteurs == nom]

    for nom in data.nomauteurs:
        publinom = data.publications[nomauteurs == nom]
        


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


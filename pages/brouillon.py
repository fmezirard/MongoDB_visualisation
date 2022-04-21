# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 22:26:51 2022

@author: florm
"""


# Page 2 - publication

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
# 2 requetes
# auteurspublications = coll.aggregate([
#                         {"$unwind": "$authors"},
#                         {"$match":{"authors.name": {"$in" : nomauteurs}, "authors.firstname": {"$in":prenomauteurs}}},
#                         {"$group": {"_id": {"name": "$authors.name",
#                                         "firstname": "$authors.firstname"},
#                                     "titre": {"$push": "$title"}}}
#                       ])          

auteurspublications = coll.aggregate([
                        {"$unwind": "$authors"},
                        {"$match":{"authors.name": {"$in" : nomauteurs}, "authors.firstname": {"$in":prenomauteurs}}},
                        {"$group": {"_id": {"name": "$authors.name",
                                        "firstname": "$authors.firstname"},
                                    "titre": {"$push": "$title"}}},
                        {"$group": {"_id": {"name": "$_id.name",
                                        "firstname": "$_id.firstname",
                                        "titre" : "$titre"}}}
                      ])    


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
  #                      {$match: {"authors.name":{$in : ['Lefèvre', 'Pacchierotti', 'Pontonnier', 'Lécuyer', 'Fromont', 'Jézéquel', 'Guillemot', 'Busnel', 'Giordano', 'Pettré', 'Maumet', 'Ferré', 'Bannier', 'Legeai', 'Olivier', 'Dumont', 'Rubino', 'Martin', 'Maillé', 'Siegel']}}},                        
  #                        {$group: {"_id": {"name": "$authors.name",
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
          
          
# Vrai requete
# db.getCollection('hal_irisa_2021').aggregate([
#                         {$unwind: "$authors"},
#                         {$group: {"_id": {"name": "$authors.name",
#                                         "firstname": "$authors.firstname"},
#                                     "publication": {$push: "$title"},
#                                     "nbpubli": {$sum: 1}}},
#                         {$sort: {"nbpubli": -1}},
#                         {$limit: 20}])


# Page3
# MONGODB OK
# db.getCollection('NYfood').aggregate([
#                         {"$unwind": "$grades"},
#                         {"$group": {"_id": {"iden": "$_id",
#                                         "grades": "$grades.grade",
#                             "coord": "$address.loc.coordinates",
#                             "borough": "$borough",
#                             "name": "$name",
#                             "cuisine": "$cuisine"},
#                                   "note_moy": {"$avg" : "$grades.score"}
#                                   }}
#                         ])


# db.getCollection('NYfood').aggregate([
#                         {"$unwind": "$grades"},
#                         {"$group": {"_id": {"iden": "$_id",
#                             "coord": "$address.loc.coordinates",
#                             "borough": "$borough",
#                             "name": "$name",
#                             "cuisine": "$cuisine"},
#                                   "lst_note": {"$push" : {"note":"$grades.grade","score":"$grades.score"}},
#                                   }}
#                         ])


# db.getCollection('NYfood').aggregate([
#                         {"$unwind": "$grades"},
#                         {"$group": {"_id": {"iden": "$_id",
#                             "notes" : "$grades.grade",
#                             "coord": "$address.loc.coordinates",
#                             "borough": "$borough",
#                             "name": "$name",
#                             "cuisine": "$cuisine"},
#                             "moy" : {"$avg": "$grades.score"} }},
                           
#                           {"$group": {"_id": {"iden": "$_id.iden",
#                             "coord": "$_id.coord",
#                             "borough": "$_id.borough",
#                             "name": "$_id.name",
#                             "cuisine": "$_id.cuisine"},
                            
#                             "lst": {"$push" : {"note":"$_id.notes","score":"$moy"}}
#                         }} 


 
# inforesto = coll.aggregate([
#                         {"$unwind": "$grades"},
#                         {"$group": {"_id": {"iden": "$_id",
#                             "notes" : "$grades.grade",
#                             "coord": "$address.loc.coordinates",
#                             "borough": "$borough",
#                             "name": "$name",
#                             "cuisine": "$cuisine"},
#                            "moy" : {"$avg": "$grades.score"} }},
                           
#                          {"$group": {"_id": {"iden": "$_id.iden",
#                             "coord": "$_id.coord",
#                             "borough": "$_id.borough",
#                             "name": "$_id.name",
#                             "cuisine": "$_id.cuisine"},
                            
#                             "lst": {"$push" : {"note":"$_id.notes","score":"$moy"}}
#                         }} 
# ])

# inforesto = coll.aggregate([
#                         {"$unwind": "$grades"},
#                         {"$group": {"_id": {"iden": "$_id",
#                             "notes" : "$grades.grade",
#                             "coord": "$address.loc.coordinates",
#                             "borough": "$borough",
#                             "name": "$name",
#                             "cuisine": "$cuisine"},
#                            "moy" : {"$avg": "$grades.score"} }},
                           
#                          {"$group": {"_id": {"iden": "$_id.iden",
#                             "coord": "$_id.coord",
#                             "borough": "$_id.borough",
#                             "name": "$_id.name",
#                             "cuisine": "$_id.cuisine"},
                            
#                             "lst": {"$push" : {"note":"$_id.notes","score":"$moy"}}
#                         }},
                           
#                          {"$group": {"_id": {"iden": "$_id.iden",
#                             "coord": "$_id.coord",
#                             "borough": "$_id.borough",
#                             "name": "$_id.name",
#                             "cuisine": "$_id.cuisine",
#                              "lst" : "$lst"}}}  
#                         ])
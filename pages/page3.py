from pymongo import MongoClient
import pandas as pd
import numpy as np
from bokeh.io import output_file, show
from bokeh.models import (BoxZoomTool, Circle, HoverTool,MultiLine, Plot, Range1d, ResetTool, ColumnDataSource, Column, Div,Row)
from bokeh.palettes import Blues8
from bokeh.plotting import figure
from bokeh.transform import linear_cmap
from bokeh.tile_providers import get_provider, Vendors


# NY food

# connection à la base de données
db_uri = "mongodb+srv://etudiant:ur2@clusterm1.0rm7t.mongodb.net/"
client = MongoClient(db_uri)
db = client["food"]

# sélection de la collection
coll = db["NYfood"]

# Requete MongoBD
# Récupération pour chaque restaurant de
# - son nom, sa cuisine, son quatier, ses coordonnees GPS
# - les notes et la moyenne pour chaque note

# La première requete qui est en commentaire suffit normalement pour récupérer
# les infos souhaitées. Cependant avec Spyder et VisualCode, il était IMPOSSIBLE
# pour nous de récupérer les infos dans la variable "lst", pour détourner ce problème
# nous avons tout regrouper avec la deuxième requete....
 
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

inforesto = coll.aggregate([
                        {"$unwind": "$grades"},
                        {"$group": {"_id": {"iden": "$_id",
                            "notes" : "$grades.grade",
                            "coord": "$address.loc.coordinates",
                            "borough": "$borough",
                            "name": "$name",
                            "cuisine": "$cuisine"},
                           "moy" : {"$avg": "$grades.score"} }},
                           
                         {"$group": {"_id": {"iden": "$_id.iden",
                            "coord": "$_id.coord",
                            "borough": "$_id.borough",
                            "name": "$_id.name",
                            "cuisine": "$_id.cuisine"},
                            
                            "lst": {"$push" : {"note":"$_id.notes","score":"$moy"}}
                        }},
                           
                         {"$group": {"_id": {"iden": "$_id.iden",
                            "coord": "$_id.coord",
                            "borough": "$_id.borough",
                            "name": "$_id.name",
                            "cuisine": "$_id.cuisine",
                             "lst" : "$lst"}}}  
                        ])

restodico = [resto["_id"] for resto in inforesto]

# Création d'un dataframe 
rows = []
for data in restodico:  
    rows.append(data) 
  
df = pd.DataFrame(rows) 


# ajout d'une colonne latitude et d'une colonne longitude
lat = []
long = []
for coor in df["coord"]:
    lat.append(coor[1])
    long.append(coor[0])
df = df.assign(longitude=long, latitude=lat)
    
#df = pd.DataFrame(zip(lat, long),columns = ['latitude','longitude'])

# Convertissons les longitudes/latitudes décimales au format Web Mercator 
def coor_wgs84_to_web_mercator(lon, lat):
    k = 6378137
    x = lon * (k * np.pi/180.0)
    y = np.log(np.tan((90 + lat) * np.pi/360.0)) * k
    return (x,y)

new_lon, new_lat = coor_wgs84_to_web_mercator(df[['longitude']], df[['latitude']])
df[['new_lon']] = new_lon
df[['new_lat']] = new_lat

# Carte
source1 = ColumnDataSource(df)

plot = figure(#x_range = (-8400000, -8000000), y_range=(4800000, 5100000),
              x_axis_type="mercator", y_axis_type="mercator",
              active_scroll='wheel_zoom', tools="pan,wheel_zoom,save,reset",
              title='Cartographie des restaurants de New-York')

tile_provider = get_provider(Vendors.CARTODBPOSITRON)
plot.add_tile(tile_provider)

plot.triangle(x='new_lon', y='new_lat', color='blue', source=source1)

hover_tool = HoverTool(tooltips=[('Quartier', '@borough'),('Nom','@name'),("Cuisine",'@cuisine'),('Notes et sa moyenne', "@lst")]) 
plot.add_tools(hover_tool)

#Ajout de code html
div = Div(text="""
<h1> Visualisation libre de données issues de NYfood </h1>
<p> La base NYfood contient des informations relatives à des restaurants de New-York. 
Pour ce troisième exercice, vous êtes libres de visualiser les données contenues dans cette base comme bon vous semble. </p>
</br>

<p> Retour à la page d'accueil : <a href="../sommaire.html">ici</a></p>

""")

layout = Column(div, plot)
output_file("page3.html")

show(layout)




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
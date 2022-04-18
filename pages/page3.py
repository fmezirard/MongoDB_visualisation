from pymongo import MongoClient
import pandas as pd
import numpy as np
from bokeh.io import output_file, show
from bokeh.models import (BoxZoomTool, Circle, HoverTool,MultiLine, Plot, Range1d, ResetTool, ColumnDataSource, Column, Div,Row)
from bokeh.palettes import Blues8
from bokeh.plotting import figure
from bokeh.transform import linear_cmap
from bokeh.tile_providers import get_provider, Vendors, CARTODBPOSITRON


# NY food

# connection à la base de données
db_uri = "mongodb+srv://etudiant:ur2@clusterm1.0rm7t.mongodb.net/"
client = MongoClient(db_uri)
db = client["food"]

# sélection de la collection
coll = db["NYfood"]

# Sélection des coordonnées des restaurants
coordonneesresto = coll.aggregate([
                        {"$unwind": "$address"},
                        {"$group": {"_id": {"iden":"$_id","coord": "$address.loc.coordinates"}}}
])  

# Récupération des coordonnées
lstcoordresto = [resto["_id"] for resto in coordonneesresto]

# Récupération des notes des resto
notesresto = coll.aggregate([
                        {"$unwind": "$grades"},
                        {"$group": {"_id": {"iden": "$_id",
                                        "grades": "$grades.grade"},
                                  "note_moy": {"$avg" : "$grades.score"}}
                          }
                        ])

# # Récupération des notes
lstnotesresto = [resto["_id"] for resto in notesresto] #lst de dico
lstnotes = [resto["note_moy"] for resto in notesresto] #lst de notes

# transformation de la liste de note en liste de dico
diconote = {}
lstnotesbis = []
for note in lstnotes:
    diconote["note"] = note
    lstnotesbis.append(diconote)

# Fusion des deux listes
[lst1.update(lst2) for lst1, lst2 in zip(lstnotesresto, lstnotesbis)]

# transformation des dictionnaires en liste
ide = []
note = []
score = []
coord = []
for dico in lstnotesresto:
    ide.append(dico["iden"])
    note.append(dico["grades"])
    score.append(dico["note"])
    coord.append(dico["coord"])

# Création d'un dataframe avec les identifiants, notes et scores moyens associé à chaque resto
df = pd.DataFrame({"identifiant": ide, "note":note,"score":score, "coordonnees":coord})
print(df)



# # Récupération des informations associées aux resto:
# inforesto = coll.find({},{"borough":1,"cuisine":1,"name":1})
    
# # Récupération des infos
# lstinforesto = []
# dicoresto = {}
# for resto in inforesto:
#     dicoresto["iden"] = resto["_id"]
#     dicoresto["borough"] = resto["borough"]
#     dicoresto["cuisine"] = resto["cuisine"]
#     dicoresto["name"] = resto["name"]
#     lstinforesto.append(dicoresto)

# # Fusion des deux listes - stockage dans la liste lstinforesto
# inforestocomplet = []
# for dico1, dico2, in zip(lstinforesto, lstcoordresto):
#     for d in (dico1, dico2):
#         for key, value in d.items():
#             dico[key]= value 
            
#             inforestocomplet.append(dico)
# #[lst1.update(lst2) for lst1, lst2 in zip(lstinforesto, lstcoordresto)]
# #inforestocomplet = {x['iden']:x for x in lstinforesto + lstcoordresto}.values()
# #merge_lists_of_dicts(lstinforesto, lstcoordresto)
# for d in (lstinforesto,lstcoordresto):
#     print(d[0])
#     for key, value in d.items():
#         print(key)  
    
# transformation en dataframe
# rows = [] 
  
# for data in lstinforesto: 
#     rows.append(data) 
  
# df = pd.DataFrame(rows)



# ajout d'une colonne latitude et d'une colonne longitude
lat = []
long = []
for coor in df["coordonnees"]:
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
df1 = pd.DataFrame()
df1[['new_lon']] = new_lon
df1[['new_lat']] = new_lat

# Carte
source1 = ColumnDataSource(df1)

plot = figure(#x_range = (-8400000, -8000000), y_range=(4800000, 5100000),
              x_axis_type="mercator", y_axis_type="mercator",
              tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',
              title='Cartographie des restaurants de New-York')

tile_provider = get_provider(CARTODBPOSITRON)
plot.add_tile(tile_provider)

plot.triangle(x='new_lon', y='new_lat', color='blue', source=source1)



hover_tool = HoverTool(tooltips=[('Note', '@note'), ('score', '@score')])
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



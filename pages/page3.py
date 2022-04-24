from pymongo import MongoClient
import pandas as pd
import numpy as np
from bokeh.io import output_file, show
from bokeh.models import (BoxZoomTool, Circle, HoverTool,MultiLine, ColorPicker, Spinner,Dropdown, CustomJS,
                          Plot, Range1d, ResetTool, ColumnDataSource, Column, Div,Row)
from bokeh.plotting import figure
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
                            
#                             "lst": {"$push" : {"note":"$_id.notes","score":"$moy"}},
#                           "moyenne" : {"$avg": "$moy"}
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
                            
                            "lst": {"$push" : {"note":"$_id.notes","score":"$moy"}},
                            "moyenne" : {"$avg": "$moy"}
                        }},
                           
                         {"$group": {"_id": {"iden": "$_id.iden",
                            "coord": "$_id.coord",
                            "borough": "$_id.borough",
                            "name": "$_id.name",
                            "cuisine": "$_id.cuisine",
                             "lst" : "$lst",
                             "moyenne": "$moyenne"}}}  
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

# Convertissons les longitudes/latitudes décimales au format Web Mercator 
def coor_wgs84_to_web_mercator(lon, lat):
    k = 6378137
    x = lon * (k * np.pi/180.0)
    y = np.log(np.tan((90 + lat) * np.pi/360.0)) * k
    return (x,y)

new_lon, new_lat = coor_wgs84_to_web_mercator(df[['longitude']], df[['latitude']])
df[['new_lon']] = new_lon
df[['new_lat']] = new_lat

# Création d'un dataframe avec toutes les notes possibles et la moyenne pour le restaurant.
dfscores = df[['iden','lst']].copy()
dfscores = dfscores.assign(scoreA=0)
dfscores = dfscores.assign(scoreB=0)
dfscores = dfscores.assign(scoreC=0)
dfscores = dfscores.assign(scoreP=0)
dfscores = dfscores.assign(scoreZ=0)
dfscores = dfscores.assign(scoreMissing=0)

for i, listededico in enumerate(dfscores.lst):
    for dico in listededico:
        if 'A' in dico.values():
            dfscores.scoreA[i] = dico["score"]
        elif 'B' in dico.values():
            dfscores.scoreB[i] = dico["score"]
        elif 'C' in dico.values():
            dfscores.scoreC[i] = dico["score"]
        elif 'P' in dico.values():
            dfscores.scoreP[i] = dico["score"]
        elif 'Z' in dico.values():
            dfscores.scoreZ[i] = dico["score"]
        else:
            dfscores.scoreMissing[i] = dico["score"]
    
# Nous fusionnons nos deux dataframes.
df = pd.merge(df, dfscores, on='iden')

# Carte
source1 = ColumnDataSource({'x':df['new_lon'],
                            'new_lat':df['new_lat'],
                            'y':df['moyenne']/3, 
                            'cuisine':df['cuisine'],
                            'name':df['name'],
                            'borough':df['borough'],
                            'lst':df['lst_x'],
                            'moyenne': df['moyenne'],
                            'moyenneGlobale': df['moyenne']/3,
                            'scoreA':df['scoreA'],
                            'scoreB':df['scoreB'],
                            'scoreC':df['scoreC'],
                            'scoreP':df['scoreP'],
                            'scoreZ':df['scoreZ'],
                            'scoreMissing':df['scoreMissing']})

plot = figure(x_axis_type="mercator", y_axis_type="mercator",
              plot_width=900, plot_height=700,
              x_range=(-15000000, 18000000),y_range=(-12000000, 15000000),
              active_scroll='wheel_zoom',
              title='Cartographie des restaurants de New-York')

tile_provider = get_provider(Vendors.CARTODBPOSITRON)
plot.add_tile(tile_provider)

points = plot.triangle(x='x', y='new_lat', color='blue', source=source1, size='y')


menu = Dropdown(label ="Choix de la taille des triangles",
                menu=[('moyenneGlobale','moyenneGlobale'),('scoreA','scoreA'),('scoreB','scoreB'),('scoreC','scoreC'),
                      ('scoreP','scoreP'),('scoreZ','scoreZ'),('scoreMissing','scoreMissing')])

# Définition des callback functions
callback = CustomJS(args=dict(source = source1), code="""
    const data = source.data;
    const val = cb_obj.item                     
    const x = data['x']
    const y = data['y']
    const ynew = data[val]
    for (let i = 0; i < x.length; i++) {
            y[i] = ynew[i]
    }
    source.change.emit();
""")

menu.js_on_event('menu_item_click', callback)

hover_tool = HoverTool(tooltips=[('Quartier', '@borough'),('Nom','@name'),("Cuisine",'@cuisine'),
                                 ('Moyenne du restaurant', "@moyenne"),('Moyenne du score choisi','@y')]) 
plot.add_tools(hover_tool)

# Color picker
# Remplissage
picker1 = ColorPicker(title="Couleur des triangles",color = points.glyph.fill_color)
picker1.js_link('color', points.glyph, 'fill_color')

# Contours
picker2 = ColorPicker(title="Couleur de contours des triangles",color=points.glyph.line_color)
picker2.js_link('color', points.glyph, 'line_color')

# Transparence
spinner2 = Spinner(title="Opacité", low=0,high=1, step=0.1, value=points.glyph.fill_alpha) 
spinner2.js_link("value", points.glyph, "fill_alpha") 

#Ajout de code html
div = Div(text="""
<h1> Visualisation libre de données issues de NYfood </h1>
<p> La base NYfood contient des informations relatives à des restaurants de New-York. 
Pour ce troisième exercice, vous êtes libres de visualiser les données contenues dans cette base comme bon vous semble. </p>
</br>

<p> Nous avons récupéré les coordonnées GPS de chaque restaurant avec leur note moyenne ainsi que
la note moyenne pour chaque note possible (A, B, C, P, Z et Not Yet Graded). </p>
<p> La taille du point est choisie par l'utilisateur selon la catégorie de la note. 
La taille pour la moyenne globale a été divisée par 3 pour que l'on puisse voir tous les points
et qu'il n'y ait pas un point qui cache tous les autres. </p>
</br>

<p> Les deux notes les plus courantes sont celles nommées A ou B. </p>
</br>

<p> Retour à la page d'accueil : <a href="../sommaire.html">ici</a></p>

""")

graph = Row(plot,Column(menu,picker1, picker2, spinner2))
layout = Column(div, graph)
output_file("page3.html")

show(layout)


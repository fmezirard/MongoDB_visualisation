from pymongo import MongoClient
import pandas as pd
from bokeh.io import output_file, show
from bokeh.models import (BoxZoomTool, Circle, HoverTool,
                          MultiLine, Plot, Range1d, ResetTool, ColumnDataSource, Column, Div,Row)
from bokeh.palettes import Blues8
from bokeh.plotting import figure
from bokeh.transform import linear_cmap


# Réseau de publications scientifiques

# connection à la base de données
db_uri = "mongodb+srv://etudiant:ur2@clusterm1.0rm7t.mongodb.net/"
client = MongoClient(db_uri)
db = client["food"]

# sélection de la collection
coll = db["NYfood"]


# MongoDB, aggregation




# Création du graphique
plot = figure(#tooltips = HOVER_TOOLTIPS,
              tools="pan,wheel_zoom,save,reset", active_scroll='wheel_zoom',
              title='NYfood')





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

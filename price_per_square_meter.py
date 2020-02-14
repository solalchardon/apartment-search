# Import all necessary packages

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from geopy.geocoders import Nominatim
import sys

# Enter criteria

address = input("Entrer l'adresse : ")
radius = input("Entrer le rayon de la zone (en mètres) : ")
start_date = input("Entrer la date de début (format AAAA-MM-JJ) : ")
end_date = input("Entrer la date de fin (format AAAA-MM-JJ) : ")
surface_min = input("Entrer la surface minimum (en m2) : ")
surface_max = input("Entrer la surface maximum (en m2) : ")
surface_min = int(surface_min)
surface_max = int(surface_max)
print("") #to skip a line after entering criteria

# Get address coordinnates

geolocator = Nominatim(user_agent="solal_chardon", timeout=1000)
location = geolocator.geocode(address)
if location == None: 
    sys.exit("Erreur : l'adresse n'existe pas.")   
lat = str(location.latitude)
lon = str(location.longitude)


# Import data from DVF API

base_url = 'http://api.cquest.org/dvf?'
url = base_url + 'lat=' + lat + '&lon=' + lon + '&dist=' + radius
r = requests.get(url)
json_data = r.json()
features = json_data['features']
results_list = []
for d in features: 
    t = d['properties']
    results_list.append(t)
raw = pd.DataFrame(results_list)
if raw.empty: 
    sys.exit("Erreur : il n'y a pas de transactions correspondant à vos critères.")

# Filter data

raw = raw.rename(columns = {'surface_relle_bati': 'surface_reelle_bati'})

raw['prix_m2'] = raw['valeur_fonciere'] / raw['surface_reelle_bati']
df = raw[(raw['date_mutation'] > (start_date)) & (raw['date_mutation'] < (end_date))]
df = df[df['type_local'] == 'Appartement']
df = df[(df['surface_reelle_bati'] > surface_min) & (df['surface_reelle_bati'] < surface_max)]
df = df[(df['prix_m2'] > 0) & (df['prix_m2'] < 30000)]

print("Il y a " + str(df.shape[0]) + " transactions correspondant à vos critères.")

# Arrange and save underlying data in Excel

ncols = [
'code_departement',
'code_postal',
'numero_voie',
'type_voie',
'voie',
'lat',
'lon',
'nombre_lots',
'surface_lot_1',
'surface_lot_2',
'surface_lot_3',
'surface_reelle_bati',
'date_mutation',
'nature_mutation',
'type_local',
'nombre_pieces_principales',
'valeur_fonciere',
'prix_m2'
]
dfs = df[ncols]

dfs.to_excel(address + ".xlsx", index = False)
print("Les données correspondant aux transactions sont enregistrées sous le nom : " + address + ".xlsx")

#Get quantiles

prix_max = int(df.prix_m2.max())
prix_med = int(df.prix_m2.median())
prix_min = int(df.prix_m2.min())
prix_q1 = int(np.percentile(df.prix_m2, 25))
prix_q3 = int(np.percentile(df.prix_m2, 75))

#Draw, save and show a swarm plot

fig= plt.figure(figsize=(8,10))
sns.swarmplot(y = 'prix_m2', data = df, size = 10)
plt.ylim(0,round(prix_max, -3) + 1000)
plt.yticks(np.arange(0, round(prix_max, -3) + 1001, 1000), fontsize = 14)
plt.ylabel('Prix au m2 (€)', fontsize = 16)
plt.title('Distribution des prix au m2', fontsize = 18)
plt.annotate(s = ('Max = ' + str(prix_max)) + ' €', xy =(0, prix_max), xytext =(0.25, prix_max), arrowprops=dict(facecolor='black'))
plt.annotate(s = ('Median = ' + str(prix_med)) + ' €', xy =(0, prix_med), xytext =(0.25, prix_med), arrowprops=dict(facecolor='black'))
plt.annotate(s = ('Min = ' + str(prix_min)) + ' €', xy =(0, prix_min), xytext =(0.25, prix_min), arrowprops=dict(facecolor='black'))
plt.annotate(s = ('Q1 = ' + str(prix_q1)) + ' €', xy =(0, prix_q1), xytext =(0.25, prix_q1), arrowprops=dict(facecolor='black'))
plt.annotate(s = ('Q3 = ' + str(prix_q3)) + ' €', xy =(0, prix_q3), xytext =(0.25, prix_q3), arrowprops=dict(facecolor='black'))

plt.savefig(fname = address + ".jpg")
print("Le graphique de distribution des prix au mètre carré est enregistré sous le nom : " + address + ".jpg")
plt.show()
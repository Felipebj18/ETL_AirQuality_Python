import pandas as pd
customer_json_file ='Datos_SIATA_Aire_pm25.json'
customers_json = pd.read_json(customer_json_file, convert_dates=True)
latitudes = customers_json.latitud.values.tolist()
longitudes = customers_json.longitud.values.tolist()
fecha = customers_json.datos[1][-1].get('fecha')
m=[]
for i in range(21):
    m.append(customers_json.datos[i][-1].get('valor'))
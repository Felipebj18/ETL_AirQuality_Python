
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.interpolate import griddata



customer_json_file ='Datos_SIATA_Aire_pm25.json'
customers_json = pd.read_json(customer_json_file, convert_dates=True)

def aqi(df):
    l_aqi = []
    #completar denominaciones
    concentraciones=df["valor"]
    l_quality = []
    for concentracion in concentraciones:
        if(concentracion<12):
            quality = "Good"
            conc_lo=0.0
            conc_hi=12.0
            aqi_lo=0.0
            aqi_hi=50
        elif(concentracion>12 and concentracion<=35.4):
            quality = "Moderate"
            conc_lo=12.1
            conc_hi=35.4
            aqi_lo=51
            aqi_hi=100
        elif(concentracion>35.4 and concentracion<=55.5):
            quality = "Unhealthy-SensitiveGroups"
            conc_lo=35.5
            conc_hi=55.4
            aqi_lo=101
            aqi_hi=150
        elif(concentracion>55.4 and concentracion<=150.4):
            quality = "Unhealthy"
            conc_lo=55.5
            conc_hi=150.4
            aqi_lo=151
            aqi_hi=200
        elif(concentracion>150.4 and concentracion<=250.4):
            quality = "Very Unhealthy"
            conc_lo=150.5
            conc_hi=250.4
            aqi_lo=201
            aqi_hi=300
        if(concentracion>250.4):
            quality = "Hazardous"
            conc_lo=250.5
            conc_hi=500.4
            aqi_lo=301
            aqi_hi=500
        aqi_equation = ((aqi_hi-aqi_lo)/(conc_hi-conc_lo)*(concentracion-conc_lo))+(aqi_lo)
        l_aqi.append(aqi_equation)
        l_quality.append(quality)
    df_aqi= pd.DataFrame({"aqi":l_aqi,"quality":l_quality})
    df_final = pd.concat([df.reset_index(),df_aqi],axis=1)
    df_final = df_final.drop(df_final.columns[[0, 1]], axis=1)
    return df_final

def transform_data(df):
    l_aux = []
    for fila in range(len(df)):
        df_datos_prueba = pd.DataFrame(df.iloc[fila]["datos"])
        df_adicional = pd.DataFrame(df.iloc[fila])
        df_adicional = df_adicional.transpose()
        df_adicional = df_adicional.drop("datos", axis=1)
        df_adicional = pd.concat([df_adicional] * len(df_datos_prueba))
        df_final = pd.concat([df_adicional.reset_index(), df_datos_prueba], axis=1)
        l_aux.append(df_final)

    dataframe_final = pd.concat(l_aux, ignore_index=True)
    dataframe_final = dataframe_final.drop(["codigoSerial", "nombreCorto", "variableConsulta", "calidad"], axis=1)
    dataframe_final['fecha'] = pd.to_datetime(dataframe_final['fecha'])
    dataframe_final['latitud'] = dataframe_final['latitud'].astype('float64')
    dataframe_final['longitud'] = dataframe_final['longitud'].astype('float64')
    dataframe_final = dataframe_final.query("0 <= valor <= 500")
    
    # Crear una nueva columna "hora" que contiene solo la hora de la fecha
    #dataframe_final['hora'] = dataframe_final['fecha'].dt.time
    dataframe_final.loc[:, 'hora'] = dataframe_final['fecha'].dt.time
    
    dataframe_final = aqi(dataframe_final)
    
    return dataframe_final

def obtener_registros_por_dia(dataframe, dia):
    dia = pd.to_datetime(dia).date()
    registros_dia = dataframe[dataframe['fecha'].dt.date == dia]
    return registros_dia

def obtener_registros_por_hora(dataframe, fecha_hora):
    fecha_hora = pd.to_datetime(fecha_hora)
    registros_hora = dataframe[dataframe['fecha'] == fecha_hora]
    return registros_hora

def change_data_types(dataframe):
    # Convierte la columna 'fecha' a datetime
    #dataframe['fecha'] = pd.to_datetime(dataframe['fecha'])
    # Convierte la columna 'hora' a time
    dataframe['hora'] = pd.to_datetime(dataframe['hora'], format='%H:%M:%S').dt.time
    return dataframe

def generate_interpolation_dataframe(dataframe):
    fecha_hora_unicas = dataframe['fecha'].unique()
    interpolations = []

    for date_time in fecha_hora_unicas:
        df_hora = obtener_registros_por_hora(dataframe, date_time)

        lat = df_hora['latitud']
        lon = df_hora['longitud']
        aqi = df_hora['aqi']

        longitud_grid = np.linspace(lon.min(), lon.max(), 100)
        latitud_grid = np.linspace(lat.min(), lat.max(), 100)
        longitud_mesh, latitud_mesh = np.meshgrid(longitud_grid, latitud_grid)

        grid_interpolado_cubico = griddata((lon, lat), aqi, (longitud_mesh, latitud_mesh), method='cubic')
        puntos_faltantes = np.isnan(grid_interpolado_cubico)
        grid_interpolado_vecinos = griddata((lon, lat), aqi, (longitud_mesh, latitud_mesh), method='nearest')
        grid_interpolado_combinado = np.where(puntos_faltantes, grid_interpolado_vecinos, grid_interpolado_cubico)

        interpolations.append(grid_interpolado_combinado)

    interpolation_df = pd.DataFrame({
        "fecha": fecha_hora_unicas,
        "interpolacion": interpolations
    })

    return interpolation_df

def calculate_daily_interpolation_means(dataframe):
    # Crear una lista para almacenar los datos de salida
    daily_means = []

    for index, row in dataframe.iterrows():
        # Obtener la fecha y la matriz de interpolación
        date = row['fecha']
        interpolation_matrix = row['interpolacion']

        # Calcular el promedio de la matriz de interpolación
        mean_interpolation = np.mean(interpolation_matrix)

        # Almacenar la fecha y el promedio en la lista de resultados
        daily_means.append([date, mean_interpolation])

    # Crear un DataFrame a partir de la lista de resultados
    daily_mean_df = pd.DataFrame(daily_means, columns=['fecha', 'promedio_interpolacion'])

    return daily_mean_df



df_final = transform_data(customers_json)
df_final['hora'] = df_final['hora'].astype(str)

df_final.to_hdf("air_quality_data.h5", key='data', format='table', mode='w')





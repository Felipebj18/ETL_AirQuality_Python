from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import numpy as np
from scipy.interpolate import griddata
from data_transformation import obtener_registros_por_hora, transform_data,change_data_types

matplotlib.use('TkAgg')  # Utiliza TkAgg como backend

def graph_aqi_animation(dataframe):
    from scipy.interpolate import griddata
    fecha_hora_unicas = dataframe['fecha'].sort_values().unique()
    for fecha in fecha_hora_unicas:
        df_hora = obtener_registros_por_hora(dataframe, fecha)
        # Definir las coordenadas de latitud y longitud en el DataFrame
        lat = df_hora['latitud']
        lon = df_hora['longitud']
        aqi = df_hora['aqi']  # Cambiamos de 'valor' a 'aqi'
        # Crear un grid de coordenadas de latitud y longitud
        latitud_grid = np.linspace(lat.min(), lat.max(), 100)  # Ajusta la resolución según tus necesidades
        longitud_grid = np.linspace(lon.min(), lon.max(), 100)  # Ajusta la resolución según tus necesidades
        latitud_mesh, longitud_mesh = np.meshgrid(latitud_grid, longitud_grid)

        # Realizar interpolación cúbica de los valores de AQI en el grid
        grid_interpolado_cubico = griddata((lat, lon), aqi, (latitud_mesh, longitud_mesh), method='cubic')
        # Encontrar los puntos en los que la interpolación cúbica no tiene valores
        puntos_faltantes = np.isnan(grid_interpolado_cubico)

        # Realizar interpolación de vecinos más cercanos en los puntos faltantes
        grid_interpolado_vecinos = griddata((lat, lon), aqi, (latitud_mesh, longitud_mesh), method='nearest')

        # Combinar las interpolaciones: usar la cúbica donde esté disponible y los vecinos más cercanos donde falte
        grid_interpolado_combinado = np.where(puntos_faltantes, grid_interpolado_vecinos, grid_interpolado_cubico)

        # Crear un gráfico de contorno del resultado combinado
        plt.figure(figsize=(12, 8))
        plt.contourf(latitud_mesh, longitud_mesh, grid_interpolado_combinado, cmap='viridis')  
        plt.plot(lat,lon,'r',ms=1)
        plt.xlabel('Latitud')
        plt.ylabel('Longitud')
        plt.title('Interpolación Cúbica con Vecinos Más Cercanos en Sectores Faltantes para AQI')
        plt.pause(0.9)
    
    plt.colorbar(label='AQI')
    plt.show()
    
air_quality_data = pd.read_hdf("air_quality_data.h5", key='data')

fig, ax = plt.subplots()


def update(frame):

    ax.clear()
    df_hora = obtener_registros_por_hora(air_quality_data, frame)
    
    lat = df_hora['latitud']
    lon = df_hora['longitud']
    aqi = df_hora['aqi']

    latitud_grid = np.linspace(lat.min(), lat.max(), 100)
    longitud_grid = np.linspace(lon.min(), lon.max(), 100)
    latitud_mesh, longitud_mesh = np.meshgrid(latitud_grid, longitud_grid)

    grid_interpolado_cubico = griddata((lat, lon), aqi, (latitud_mesh, longitud_mesh), method='cubic')
    puntos_faltantes = np.isnan(grid_interpolado_cubico)
    grid_interpolado_vecinos = griddata((lat, lon), aqi, (latitud_mesh, longitud_mesh), method='nearest')
    grid_interpolado_combinado = np.where(puntos_faltantes, grid_interpolado_vecinos, grid_interpolado_cubico)

    ax.contourf(latitud_mesh, longitud_mesh, grid_interpolado_combinado, cmap='viridis')
    ax.set_xlabel('Latitud')
    ax.set_ylabel('Longitud')
    ax.set_title(f'Interpolación Cúbica con Vecinos Más Cercanos en Sectores Faltantes para AQI {frame}')
    

fecha_hora_unicas = air_quality_data['fecha'].sort_values().unique()

ani = FuncAnimation(fig, update, frames=fecha_hora_unicas, repeat=False,interval=100)

plt.show()
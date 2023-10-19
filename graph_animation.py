from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
import numpy as np
from scipy.interpolate import griddata
from data_transformation import obtener_registros_por_hora, transform_data, change_data_types

matplotlib.use('TkAgg')  # Utiliza TkAgg como backend

air_quality_data = pd.read_hdf("air_quality_data.h5", key='data')

fig, ax = plt.subplots()

def update(frame):
    ax.clear()
    df_hora = obtener_registros_por_hora(air_quality_data, frame)
    
    lat = df_hora['latitud']
    lon = df_hora['longitud']
    aqi = df_hora['aqi']

    # Intercambia latitud y longitud en el siguiente bloque
    longitud_grid = np.linspace(lon.min(), lon.max(), 100)
    latitud_grid = np.linspace(lat.min(), lat.max(), 100)
    longitud_mesh, latitud_mesh = np.meshgrid(longitud_grid, latitud_grid)

    #interpolado combinado
    grid_interpolado_cubico = griddata((lon, lat), aqi, (longitud_mesh, latitud_mesh), method='cubic')
    puntos_faltantes = np.isnan(grid_interpolado_cubico)
    grid_interpolado_vecinos = griddata((lon, lat), aqi, (longitud_mesh, latitud_mesh), method='nearest')
    grid_interpolado_combinado = np.where(puntos_faltantes, grid_interpolado_vecinos, grid_interpolado_cubico)

    ax.contourf(longitud_mesh, latitud_mesh, grid_interpolado_combinado, cmap='YlOrRd')  
    ax.set_xlabel('Longitud')
    ax.set_ylabel('Latitud')
    ax.set_title(f'Interpolación Cúbica con Vecinos Más Cercanos en Sectores Faltantes para AQI {frame}')

fecha_hora_unicas = air_quality_data['fecha'].sort_values().unique()

ani = FuncAnimation(fig, update, frames=fecha_hora_unicas, repeat=False, interval=100)

plt.show()

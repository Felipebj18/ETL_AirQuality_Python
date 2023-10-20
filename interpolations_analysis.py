import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

daily_contamination = pd.read_hdf("daily_contamination.h5")
print(daily_contamination)
fechas = daily_contamination['fecha']
promedios_interpolaciones = daily_contamination['promedio_interpolacion']

plt.figure(figsize=(12, 6))
plt.scatter(daily_contamination.index, daily_contamination['promedio_interpolacion'], c=daily_contamination['promedio_interpolacion'] > 100, cmap='coolwarm', label='Contaminación promedio')
plt.xlabel('Fecha')
plt.ylabel('Contaminación promedio')
plt.title('Promedio de Contaminación por Fecha')
plt.legend()
plt.xticks(rotation=45)
plt.axhline(y=100, color='red', linestyle='--', label='Umbral 100')
plt.show()
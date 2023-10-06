#importando la libreria
import numpy as np
#creo mi funcion base (es la que conozco, es mi modelo conocido)
def func(x, y):
 return x*(1-x)*np.cos(4*np.pi*x) * np.sin(4*np.pi*y**2)**2
#creo una malla de 100 x 200
grid_x, grid_y = np.mgrid[0:1:100j, 0:1:200j]
#me invento un grupo de puntos aleatorios
points = np.random.rand(100, 2)
#de estos puntos que serian los sensores, y sus lecturas, voy a interpolar en
#la malla los valores que deseo calcular para mi modelo de deduccion real
values = func(points[:,0], points[:,1])
# ejecuto las interpolaciones, uso tres metodos para comparar su desempeno
from scipy.interpolate import griddata
grid_z0 = griddata(points, values, (grid_x, grid_y), method='nearest')
grid_z1 = griddata(points, values, (grid_x, grid_y), method='linear')
grid_z2 = griddata(points, values, (grid_x, grid_y), method='cubic')


#grafico los resultados de los tres ejemplos de inteprolacion
import matplotlib.pyplot as plt
plt.subplot(221)
plt.imshow(func(grid_x, grid_y).T, extent=(0,1,0,1), origin='lower')
plt.plot(points[:,0], points[:,1], 'k.', ms=1)
plt.title('Original')
plt.subplot(222)
plt.imshow(grid_z0.T, extent=(0,1,0,1), origin='lower')
plt.title('Nearest')
plt.subplot(223)
plt.imshow(grid_z1.T, extent=(0,1,0,1), origin='lower')
plt.title('Linear')
plt.subplot(224)
plt.imshow(grid_z2.T, extent=(0,1,0,1), origin='lower')
plt.title('Cubic')
plt.gcf().set_size_inches(6, 6)
plt.show()

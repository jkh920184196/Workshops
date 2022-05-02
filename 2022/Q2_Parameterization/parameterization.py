from pyaedt import Hfss

hfss = Hfss(specified_version='2022.1', designname='case1')

hfss['Nx'] = '4'
hfss['wx'] = '1mm'
hfss['wy'] = '10mm'
u=1

models = []
for i in range(100):
    x = hfss.modeler.create_rectangle(2,
                                      [f'if(Nx>{i}, {u}*wx, wx)','0mm','0mm'],
                                      [f'if(Nx>{i}, {i+1}*wx, wx)', 'wy'],
                                      name='rect')
    x.color = (255,0,0)
    u+=i+2
    models.append(x)

hfss.modeler.unite(models)

#%%

from pyaedt import Hfss

hfss = Hfss(specified_version='2022.1', designname='case2')

hfss['Nr'] = 4
hfss['dr'] = '1mm'
hfss['dz'] = '1mm'
hfss['ratio'] = 0.7

rings = []
for i in range(0, 20):
    c1 = hfss.modeler.create_circle(2, (0, 0, f'if({i}<Nr, {i}*dz, 0)'), f'if({i}<Nr, {2*i+1}*dr, 1*dr)', is_covered=False, name=f'c_{2*i}')
    c2 = hfss.modeler.create_circle(2, (0, 0, f'if({i}<Nr, ({i}+ratio)*dz, ratio*dz)'), f'if({i}<Nr, {2*i+2}*dr, 2*dr)', is_covered=False, name=f'c_{2*i+1}')
    ring = hfss.modeler.connect([c1, c2])

sheets = hfss.modeler.get_objects_in_group('Sheets')
hfss.modeler.unite(sheets)

#%%

hfss = Hfss(specified_version='2022.1', designname='case3')
N=4

hfss['dx'] = '4mm'
hfss['dy'] = '3mm'
hfss['dz1'] = '0.2mm'
hfss['dz2'] = '0.1mm'
hfss['configuration'] = [1]*(N**2)


create_rectangle = hfss.modeler.create_rectangle
keys = [(i, j) for i in range(N) for j in range(N)]

x = create_rectangle(2, ('0mm', '0mm', '0mm'), (f'{N}*dx', f'{N}*dy'), name = 'm0')
hfss.modeler.thicken_sheet(x, 'dz2')
for n, (nx, ny) in enumerate(keys):
        x = create_rectangle(2,
                             (f'if(configuration[{n}]==1, {nx}*dx, 0)', f'if(configuration[{n}]==1, {ny}*dy, 0)', f'if(configuration[{n}]==1, 1mm, 0mm)'), 
                             (f'if(configuration[{n}]==1, dx, {N}*dx)', f'if(configuration[{n}]==1, dy, {N}*dy)'), name=f'mp{nx}_{ny}_0')
        hfss.modeler.thicken_sheet(x, f'if(configuration[{n}]==1, dz1, dz2)')

#%%
from pyaedt import Hfss
hfss = Hfss(specified_version='2022.1', designname='case4')

hfss['Nr'] = 6
hfss['R0'] = '100um'
hfss['W0'] = '20um'
hfss['Pitch'] = '40um'
hfss['Nn'] = 4
hfss['T0'] = '5um'


locations = []
for i in range(200):
    locations.append((f'if({i}<Nr*Nn, (R0+(Pitch/cos(pi/Nr))*{i}/Nr)*cos(2*pi*{i}/Nr), (R0+(Pitch/cos(pi/Nr))*Nn)*cos(2*pi*Nn))', 
                      f'if({i}<Nr*Nn, (R0+(Pitch/cos(pi/Nr))*{i}/Nr)*sin(2*pi*{i}/Nr), (R0+(Pitch/cos(pi/Nr))*Nn)*sin(2*pi*Nn))',
                      '0mm'))
    
hfss.modeler.create_polyline(locations, xsection_type='Line', xsection_width='W0', name='spiral')
hfss.modeler.thicken_sheet('spiral', 'T0' )

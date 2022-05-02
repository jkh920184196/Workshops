#匯入模組
import matplotlib.pyplot as plt
from pyaedt import Hfss
from scipy.optimize import minimize

#開啟HFSS
hfss = Hfss(specified_version='2022.1')

#初始化HFSS參數
hfss['Wp'] = '5.35mm'
hfss['Lp'] = '4.54mm'
hfss['Ws1'] = '0.5mm'
hfss['Ws2'] = '0.5mm'
hfss['Ws3'] = '0.5mm'
hfss['Ws4'] = '0.5mm'
hfss['Wf']= '1mm'
hfss['Lf'] = '3mm'
hfss['Tm'] = '0.1mm'
hfss['Ts'] = '1mm'

hfss['dx'] = '10mm'
hfss['dy'] = '10mm'
hfss['P'] = '1mm'

#定義天線右半邊座標點
half_patch = [('0mm', '0mm'),
              ('Wf/2', '0mm'),
              ('Wf/2', 'Lf'),
              ('Wp/2', 'Lf'),
              ('Wp/2', 'Lf+Lp'),
              ('0mm', 'Lf+Lp'),
              ('0mm', 'Lf+Lp-Ws1'),
              ('Wp/2-Ws1-Ws2-Ws3', 'Lf+Lp-Ws1'),
              ('Wp/2-Ws1-Ws2-Ws3', 'Lf+Ws1+Ws2+Ws3'),
              ('Wp/2-Ws1-Ws2-Ws3-Ws4', 'Lf+Ws1+Ws2+Ws3'),
              ('Wp/2-Ws1-Ws2-Ws3-Ws4', 'Lf+Lp-Ws1-Ws4'),
              ('0mm', 'Lf+Lp-Ws1-Ws4'),
              ('0mm', 'Lf+Ws1+Ws2'),
              ('Wp/2-Ws1-Ws2','Lf+Ws1+Ws2'),
              ('Wp/2-Ws1-Ws2', 'Lf+Lp-Ws1'),
              ('Wp/2-Ws1','Lf+Lp-Ws1'),
              ('Wp/2-Ws1','Lf+Ws1'),
              ('0mm','Lf+Ws1'),]

#加入Z座標點
half_patch = [(i, j , '0mm') for i, j in half_patch]

#產生多邊形
x1 = hfss.modeler.create_polyline(half_patch, cover_surface=True, matname='copper')

#複製到左半邊
x2 = hfss.modeler.duplicate_and_mirror(x1, (0, 0, 0), (1, 0, 0))

#合併左右半邊
x = hfss.modeler.unite([x1.name, x2[1][0]])

#生成厚度
hfss.modeler.thicken_sheet(x1, 'Tm')

#生成sheet，之後可在其上設port
sheet = hfss.modeler.create_rectangle(1, ('-Wf/2', '0mm', '0mm') , ('-Ts', 'Wf'))

#%%

#定義陣列大小
Nx = 1
Ny = 1

#複製單元到相對位置
for i in range(Nx):
    for j in range(Ny):
        if i + j != 0:
            hfss.modeler.duplicate_along_line([x1.name, sheet.name], (f'dx*{i}', f'dy*{j}', '0mm'))

#%%
fc = '35GHz'

#設定基板
p0 = ('-Wp/2-P', '-P', '0mm')
size = (f'({Nx}-1)*dx+Wp+2*P', f'({Ny}-1)*dy+(Lf+Lp)+2*P', '-Ts')
substrate = hfss.modeler.create_box(p0, size, matname='FR4_epoxy')

#將基板底部設定為PEC
hfss.assign_perfecte_to_sheets(substrate.bottom_face_z)

#找出所有sheets並在上面設定ports
for n, i in enumerate(hfss.modeler.get_objects_in_group('Sheets'), 1):
    port = hfss.create_lumped_port_to_sheet(i, 2, portname=f'port{n}')

#設定Open Region
hfss.create_open_region(fc)

#%%

#設定Solution Setup
setup = hfss.create_setup('setup1')
setup.props['Frequency'] = fc
setup.props['MaximumPasses'] = 20
setup.update()

#設定Sweep
sweep = setup.add_sweep('sweep1')
sweep.props['RangeStart'] = '30GHz'
sweep.props['RangeEnd'] = '40GHz'
sweep.update()

#%%
#啟動模擬，可指定CPU核心數
hfss.analyze_nominal(4)

#抓取資料
RL = hfss.post.get_report_data('dB(S11)')
y = RL.data_real()
x = RL.sweeps['Freq']
plt.plot(x, y)
plt.grid()
plt.show()


#%% 優化一：使用外部Scipy優化引擎

#定義目標函數
def target(parameters):
    print(parameters)
    Ws1, Ws2, Ws3, Ws4 = parameters
    hfss['Ws1'] = f'{Ws1}mm'
    hfss['Ws2'] = f'{Ws2}mm'
    hfss['Ws3'] = f'{Ws3}mm'
    hfss['Ws4'] = f'{Ws4}mm'
    
    hfss.analyze_nominal(4)

    RL = hfss.post.get_report_data('dB(S11)')
    y = RL.data_real()
    x = RL.sweeps['Freq']
    plt.title(str(parameters))
    plt.plot(x, y)
    plt.grid()
    plt.show()
    
    result = hfss.post.get_report_data('dB(S11)')
    
    print(result.data_real()[0])
    return result.data_real()[0]

#初始值
x0 = [0.5, 0.5, 0.5, 0.5]

#數值範圍
bnds = ((0.35, 0.65), (0.35, 0.65), (0.35, 0.65), (0.35, 0.65))

#啟動優化
sol = minimize(target, x0, bounds = bnds, tol=1e-6, options = {'maxiter':100, 'disp':True})
print(sol)

#%% 優化二：使用HFSS內部優化引擎

定義目標
optim = hfss.optimizations.add(calculation="dB(S(1,1))", ranges={"Freq": fc}, condition='<', goal_value=-20)
optim.props['AnalysisStopOptions']['MaxNumIteration'] = 20

#定義數值範圍
optim.add_variation('Ws1', 0.35, 0.65)
optim.add_variation('Ws2', 0.35, 0.65)
optim.add_variation('Ws3', 0.35, 0.65)
optim.add_variation('Ws4', 0.35, 0.65)

#啟動模擬
hfss.analyze_setup(optim.name, num_cores=4, num_tasks=4)

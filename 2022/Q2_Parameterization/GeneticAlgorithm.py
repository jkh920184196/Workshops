import math
import numpy as np
import itertools
import random
import matplotlib.pyplot as plt

#格雷編碼生成函數
def generate_gray(n):
    result = ["0", "1"]
    i = 2
    j = 0
    while(True): 
        if i >= 1 << n:
            break

        for j in range(i - 1, -1, -1):
            result.append(result[j])
 
        for j in range(i):
            result[j] = "0" + result[j]
 
        for j in range(i, 2 * i):
            result[j] = "1" + result[j]
        
        i = i << 1
    return result

#目標函數定義
def target(data):
    x, y = data
    result = (3*(1-x)**2*math.exp(-x**2-(y+1)**2)
              -10*(x/5-x**3-y**5)*math.exp(-x**2-y**2)
              -1/3*math.exp(-(x+1)**2-y**2))
    return result

#優化設定參數
population_size = 50
variable_range = [(-4, 4), (-4, 4)]
bit_length = [7, 7]
generation_count = 500


#生成編碼與變數集合對應字典
pool = {}
values = []
grays = []
for n, (vmin, vmax) in enumerate(variable_range):
    x = np.linspace(vmin, vmax, 2**bit_length[n])
    values.append(x)
    gray = generate_gray(bit_length[n])
    grays.append(gray)
    
samples = list(itertools.product(*values))
codes = [i+j for i, j in itertools.product(*grays)]

dict1 = dict(zip(samples, codes))
dict2 = dict(zip(codes, samples))

#生成初代基因群並計算適配值
#population = random.sample(codes, population_size)
step = int(len(codes)/population_size)
population = codes[::step]
for i in population:
    pool[i] = target(dict2[i])

# max:8.10
#依據機率挑選配對及突變以生成子體並其計算適配值後加入群體
iteration = []
for gen in range(generation_count):
    # for x, y in [dict2[i] for i in pool]:
    #     plt.scatter(x, y, color='g')
    #     plt.xlim(-3,3)
    #     plt.ylim(-3,3)
    # plt.show()
    
    print(dict2[max(pool, key=pool.get)])
    print(max(pool.values()))
    iteration.append(max(pool.values()))
    
    v_max = max(pool.values())
    v_min = min(pool.values())
    
    pr = {k:((v-v_min)/(v_max-v_min))**2 for k, v in pool.items()}
    k_list, v_list = zip(*pr.items())
    
    father, mother = random.choices(k_list, weights=v_list, k=2)
    

    child = ''
    for i, j in zip(father, mother):
        gene = random.choices([i, j])
        child += gene[0]
            
    if child not in pool:
        pool[child] = target(dict2[child])

    n = random.randrange(len(father))
    
    if father[n] == 0:
        mutation = father[:n] + '1' + father[n+1:]
    else:
        mutation = father[:n] + '0' + father[n+1:]
        
    if mutation not in pool:
        pool[mutation] = target(dict2[mutation])            
          
plt.ylim(0,9)
plt.grid()
plt.plot(iteration)
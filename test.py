import time
from tqdm import tqdm

for i in tqdm(range(10), desc='Pages', colour='red'):
    time.sleep(1)
    for j in tqdm(range(10), desc='Ads', colour='blue'):
        time.sleep(1)
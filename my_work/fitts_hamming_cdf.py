import numpy as np
from pylab import *

from numpy import cumsum

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import math



output_folder = '../accessibility_api_files/output/'


hamming = []
fitts = []

import csv
with open(output_folder + 'pairwise_data_GT_no_shortcut.csv', newline='') as csvfile:
    lines = csv.reader(csvfile, delimiter=',')
    i=0
    for row in lines:
        i += 1

        if(i == 1):
            continue 
        hamming.append(math.log(float(row[2]), 2))
        # hamming.append(float(row[2]))

        if(float(row[3]) >= 0):
            fitts.append(float(row[3]))
        


print(len(fitts), len(hamming))


# max_fitts = max(fitts)
# max_hamming = max(hamming)


# for i in range(len(fitts)):
#     fitts[i]/=max_fitts

# for i in range(len(hamming)):
#     hamming[i]/=max_hamming     


sum_fitts = sum(fitts)
sum_hamming = sum(hamming)


pdf_fitts_arr = fitts[:]
pdf_hamming_arr = hamming[:]

for i in range(len(fitts)):
    pdf_fitts_arr[i] /= sum_fitts

for i in range(len(hamming)):
    pdf_hamming_arr[i] /= sum_hamming


cdf_fitts_arr = cumsum(pdf_fitts_arr)
cdf_hamming_arr = cumsum(pdf_hamming_arr)



# plot(fitts, cdf_fitts_arr)

# show()




count_fitts, bins_count_fitts = np.histogram(fitts, bins=1000)
pdf_fitts = count_fitts / sum(count_fitts)
cdf_fitts = np.cumsum(pdf_fitts)

count_hamming, bins_count_hamming = np.histogram(hamming, bins=1000)
pdf_hamming = count_hamming / sum(count_hamming)
cdf_hamming = np.cumsum(pdf_hamming)
  

print(bins_count_fitts[1:], cdf_fitts)


# plotting PDF and CDF
# plt.plot(bins_count_fitts[1:], pdf_fitts, color="red", label="PDF")
plt.plot(bins_count_fitts[1:], cdf_fitts, color= "red", label="fitts")
plt.plot(bins_count_hamming[1:], cdf_hamming, color="blue", label="hamming")
plt.legend()

plt.show()
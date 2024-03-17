'''
Unreliable medium: Probably 50%
Window Size: 4
Total number of transmitted packets:  724
Number of retransmitted packets:  292
Time taken to complete file transfer:  74.54184317588806
Number of timeouts:  73

Window Size: 8
Total number of transmitted packets:  1117
Number of retransmitted packets:  685
Time taken to complete file transfer:  88.23038840293884
Number of timeouts:  86

Window Size: 12
Total number of transmitted packets:  1525
Number of retransmitted packets:  1093
Time taken to complete file transfer:  95.04869055747986
Number of timeouts:  92

Window Size: 16
Total number of transmitted packets:  1980
Number of retransmitted packets:  1548
Time taken to complete file transfer:  101.811678647995
Number of timeouts:  98

Window Size: 24
Total number of transmitted packets:  3000
Number of retransmitted packets:  2568
Time taken to complete file transfer:  115.61076951026917
Number of timeouts:  110
'''
import matplotlib.pyplot as plt

WINDOW_SIZE = "Window Size"

# a. Window size (N) vs. time taken to complete file transfer
window_size = [4, 8, 12, 16, 24]      # X-Axis: window size
transmission_times = [74, 88, 95, 101, 115]  # Y-Axis: transmission time

# Creating the first figure and plot (a. Transmission Time)
plt.figure(figsize=(10, 5))
plt.plot(window_size, transmission_times, marker='o', color='blue', linestyle='-')
plt.xlabel(WINDOW_SIZE)
plt.ylabel("Transmission Time")
plt.title("GBN Measurements - Transmission Time")
plt.grid(True)
plt.show()

# b. Window size (N) vs. # of retransmissions
number_of_retransmissions = [292, 685, 1093, 1548, 2568]

# Creating the second figure and plot (b. # of Retransmissions)
plt.figure(figsize=(10, 5))
plt.plot(window_size, number_of_retransmissions, marker='o', color='orange', linestyle='-')
plt.xlabel(WINDOW_SIZE)
plt.ylabel("# of Retransmissions")
plt.title("GBN Measurements - Retransmissions")
plt.grid(True)
plt.show() 

# c. Window size (N) vs. # of timeout
number_of_timeouts = [73, 86, 92, 98, 110]

# Creating the third figure and plot (c. # of Timeouts)
plt.figure(figsize=(10, 5))
plt.plot(window_size, number_of_timeouts, marker='o', color='green', linestyle='-')
plt.xlabel(WINDOW_SIZE)
plt.ylabel("# of Timeout")
plt.title("GBN Measurements - Timeouts")
plt.grid(True)
plt.show() 

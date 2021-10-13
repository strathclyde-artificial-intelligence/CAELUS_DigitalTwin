from statistics import mean
from .charge_prof import charge_prof

# %% Read Input for Landings
# landings = [[2021 08 17 00 00 00] 60 1;
#             [2021 08 17 01 00 00] 60 1;
#             [2021 08 17 02 00 00] 99 1;
#             [2021 08 17 03 00 00] 20 2;
#             [2021 08 17 04 00 00] 90 1;
#             [2021 08 17 05 00 00] 50 2;
#             [2021 08 17 06 00 00] 30 1;
#             [2021 08 17 07 00 00] 10 1;
#             [2021 08 17 08 00 00] 90 1;
#             [2021 08 17 09 00 00] 80 2;
#             [2021 08 17 10 00 00] 50 1;
#             [2021 08 17 11 00 00] 10 0.5;
#             [2021 08 17 12 00 00] 60 1;
#             [2021 08 17 13 00 00] 60 1;
#             [2021 08 17 14 00 00] 99 1;
#             [2021 08 17 15 00 00] 20 2;
#             [2021 08 17 16 00 00] 90 1;
#             [2021 08 17 17 00 00] 50 2;
#             [2021 08 17 18 00 00] 30 1;
#             [2021 08 17 19 00 00] 10 1;
#             [2021 08 17 20 00 00] 90 1;
#             [2021 08 17 21 00 00] 80 2;
#             [2021 08 17 22 00 00] 50 1;
#             [2021 08 17 23 00 00] 10 0.5
#             ];
 
# %         landings = [[2021 08 17 00 00 00] 99 1
# %             ];

"""
Make the timestamp right
"""
from calendar import monthrange
import datetime
def balance_time(timestamp_array):
    normalised_array = [
        timestamp_array[0],
        min((timestamp_array[1]), 12),
        min(timestamp_array[2], monthrange(timestamp_array[0], timestamp_array[1])[1]),
        min(timestamp_array[3], 24),
        min(timestamp_array[4], 59),
        min(timestamp_array[5], 59)
    ]
    delta = datetime.timedelta(
        days=max(0,timestamp_array[2] - monthrange(timestamp_array[0], timestamp_array[1])[1]),
        hours=max(0,timestamp_array[3] - 24),
        minutes=max(0, timestamp_array[4] - 59),
        seconds=max(0,timestamp_array[5] - 59)
    )
    date = datetime.datetime(*normalised_array) + delta
    return [date.year, date.month, date.day, date.hour, date.minute, date.second]


def hour(timestamp_array):
    return timestamp_array[3]
    
def demand_schedule(landings, base_load = 0):
    #  Define Auxilliary (Base Load)

    # Build Demand Profile
    GC_temp = []
    GC_prof = []
    GC_prof_temp = []
    for x in range(24):
        # 0 hour profile
        # 1 Average power profile
        # 2 Peak power profile
        # 3 Energy Profile
        GC_prof.append([x, 0, 0, 0])
        GC_prof_temp.append([x, 0, 0, 0])

    for i in range(len(landings)):
        
        tstart, DoD, Crate = landings[i]
        GC_temp = charge_prof(tstart, DoD, Crate) 
        
        avg_power_prof = [row[1] for row in GC_temp]
        mean_power = mean(avg_power_prof)
        max_power = max(avg_power_prof)

        for j in range(len(GC_temp)):
            tstamp = balance_time(GC_temp[j][0])
            GC_prof_temp[hour(tstamp)][1] = mean_power # Update Average Power
            GC_prof_temp[hour(tstamp)][2] = max_power # Update Peak Power Demand
            GC_prof_temp[hour(tstamp)][3] = GC_prof_temp[hour(tstamp)][3] + GC_temp[j][2] # Update Energy Demand

        custom_add = lambda r0, r1: [r0[0]] + [a+b for a,b in zip(r0[1:], r1[1:])]
        GC_prof = [
            custom_add(gc_prof_row, gc_prof_temp_row) for gc_prof_row, gc_prof_temp_row in zip(GC_prof, GC_prof_temp)
        ]
        
    return GC_prof

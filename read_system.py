import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


"""
This function receives a text file that is of format of a table that represents partial data of a 
binary system composed of a white dwarf and a companion object.
The system undergoes an accretion process which ends in a nova eruption in each cycle
The table has 4 columns that are relevent for the analysis:
- The cycle number
- The time
- The effective temperature
- The accreted mass, if the system is undergoing an eruption the value in this column would be negative
@return a dataframe that consists of these 4 columns.
"""
def read_file(file_name):
    df = pd.read_csv(file_name, sep="\s+", header=None)
    df = df.iloc[0:, [1, 7, 8, 14]]
    df.rename(columns={df.columns[0]: "cycle"}, inplace=True)
    df.rename(columns={df.columns[1]: "time"}, inplace=True)
    df.rename(columns={df.columns[2]: "temperature"}, inplace=True)
    df.rename(columns={df.columns[3]: "Accreted mass"}, inplace=True)
    df["cycle"] = pd.to_numeric(df["cycle"], errors='coerce')
    df["time"] = pd.to_numeric(df["time"], errors='coerce')
    df["temperature"] = pd.to_numeric(df["temperature"], errors='coerce')
    df["Accreted mass"] = pd.to_numeric(df["Accreted mass"], errors='coerce')
    return df


"""
This function receives a list of files, each one of them consisits of cycles of the system's evolution
and merges them into one dataframe.
"""
def concatenate_files(lst):
    df = read_file(lst[0])
    max_cycle = df["cycle"].max()
    max_time = df["time"].max()
    for i in range(1, len(lst)):
        df2 = read_file(lst[i])
        df2["cycle"] += max_cycle
        df2["time"] += max_time
        max_cycle += df2["cycle"].max()
        max_time += df2["time"].max()
        df = pd.concat([df, df2], ignore_index=True)   
    return df


"""
Receiving a dataframe that represent a binary system, this function finds the phases of the temperature
decay after an outburst has finished(when the white dwarf finishes ejecting mass), and returns a dictionary.
Each key in it is the cycle number and its a value is a list whose members are the row numbers that are the 
start and the of the phase.
**To be more precise the cycle number is not the same one that is given to us in the table.
The decay starts in a particular cycle and continues into the next one, until temperature starts to
arise. 
"""
def find_delimiters(df):
    result = dict()
    max_cycle = df["cycle"].max()
    for cycle in range(1, max_cycle):
        last_row = df[df["cycle"] == cycle].index[-1]
        for row in range(last_row, 0, -1):
            if df.iloc[row, 3] < 0:
                delimiter_1 = row
                break
        for row in range(last_row, 500+last_row):        
            if df.iloc[row, 2] > df.iloc[row-1, 2]:
                delimiter_2 = row
                break
        result[cycle] = [delimiter_1, delimiter_2]
    return result


"""
This function plots the effective temperature accoss many cycles for the given system.
The cycles were chosen manually at this point.
An algorithm to automate this process is to be implemented.
"""
def draw_cycles(df, cycles_list):
    cycles_dict = find_delimiters(df)
    plt.xlabel("time (years in log10)")
    plt.ylabel("temperature   (log K)")
    for cycle in cycles_list:
        delimiter_1, delimiter_2 = cycles_dict[cycle]
        phase = df.iloc[delimiter_1:delimiter_2]
        phase["time"] = phase["time"] - phase["time"].min()
        phase["time"] = np.log10(phase["time"])
        xpoints = phase["time"]
        ypoints = phase["temperature"]
        plt.scatter(xpoints, ypoints, label="cycle " + str(cycle))
        plt.legend()
    plt.show()


"""
# Testing block
if __name__ == '__main__':
    lst = ["l_045_025_A", "l_044_019_B"]
    df = concatenate_files(lst)
    # print(find_delimiters(df))
    cycles_dict = find_delimiters(df)
    # print(cycles_dict)
    draw_cycle(df, cycles_dict, 90)
    draw_cycle(df, cycles_dict, 190)
"""

# -*- coding: utf-8 -*-
"""

Created on 19.11.2018
@author: sram
Tire Wear Model for Switzerland

"""

### Productionvolume diagram
import numpy as np

# import pandas as pd
import matplotlib.pyplot as plt

# import matplotlib.lines as mlines
# from scipy.stats import gaussian_kde


### PLOT ALL OUTFLOWS #########################################################

# compartment with loggedOutflows
loggedOutflows = simulator.getLoggedOutflows()

# loop over the list of compartments with loggedoutflows
for Comp in loggedOutflows:
    print "Flows from " + Comp.name + ":"

    # in this case name is the key, value is the matrix(data), in this case .items is needed
    for comp, data in Comp.outflowRecord.items():
        print " --> " + str(comp) + ": Mean = " + str(
            round(np.mean(data[:, Speriod]), 0)
        ) + " ± " + str(round(np.std(data[:, Speriod]), 0))

        mean = []
        q25 = []
        q75 = []
        minimum = []
        maximum = []

        for i in range(0, np.shape(data)[1]):
            mean.append(np.mean(data[:, i]))
            q25.append(np.percentile(data[:, i], 25))
            q75.append(np.percentile(data[:, i], 75))
            minimum.append(np.min(data[:, i]))
            maximum.append(np.max(data[:, i]))

        # create a new figure
        fig = plt.figure("FLOW_" + Comp.name + " to " + comp)
        plt.xlabel("Year", fontsize=14)
        plt.ylabel("Flow mass (t)", fontsize=14)
        plt.rcParams["font.size"] = 12  # tick's font
        plt.xlim(xmin=1984.5, xmax=2016.5)
        xScale = np.arange(1985, 2017)
        plt.fill_between(
            xScale, minimum, maximum, color="blanchedalmond", label="Range"
        )
        plt.plot(xScale, mean, color="darkred", linewidth=2, label="Mean Value")
        plt.plot(
            xScale,
            q25,
            color="red",
            linestyle="dashed",
            linewidth=1.5,
            label="25% Quantile",
        )
        plt.plot(
            xScale,
            q75,
            color="red",
            linestyle="dashed",
            linewidth=1.5,
            label="75% Quantile",
        )
        plt.legend(loc="upper left", fontsize="small")

        fig.savefig(
            "Graphs Tire Wear/TimeSeries_Tire" + Comp.name + " to " + comp + ".pdf",
            bbox_inches="tight",
        )

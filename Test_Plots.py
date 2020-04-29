# -*- coding: utf-8 -*-

import os
import numpy as np
import matplotlib.pyplot as plt

import Test_Runner as res


### PLOT ALL OUTFLOWS #########################################################

# compartment with loggedOutflows
loggedOutflows = res.simulator.getLoggedOutflows()

# loop over the list of compartments with loggedoutflows
for Comp in loggedOutflows:

    for comp, data in Comp.outflowRecord.items():

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
        plt.title("Flow from " + Comp.name + " to " + comp)
        plt.rcParams["font.size"] = 12  # tick's font
        plt.xlim(xmin=res.startYear - 0.5, xmax=res.startYear + res.Tperiods - 0.5)
        xScale = np.arange(res.startYear, res.startYear + res.Tperiods)

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
            os.path.join(
                "experiment_output/TimeSeries_" + Comp.name + "_to_" + comp + ".pdf"
            ),
            bbox_inches="tight",
        )

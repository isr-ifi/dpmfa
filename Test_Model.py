# -*- coding: utf-8 -*-
"""
Created on 19.11.2018
@author: sram
Tire Wear Flow Model for Switzerland 1988 - 2018
"""
### PACKAGE IMPORT AND VARIABLE DEFINITION ################################################################################################################################

# import necessary packages
from dpmfa import components as cp
from dpmfa import model
import numpy.random as nr
import numpy as np

# create model
model = model.Model("Simple Experiment for Testing")

RUNS = 10

### COMPARTMENT DEFINITION ################################################################################################################################################

Inflow1 = cp.FlowCompartment("Inflow1", logInflows=True, logOutflows=True)
Inflow2 = cp.FlowCompartment("Inflow2", logInflows=True, logOutflows=True)

Stock1 = cp.Stock("Stock1", logInflows=True, logOutflows=True, logImmediateFlows=True)
Flow1 = cp.FlowCompartment("Flow1", logInflows=True, logOutflows=True)

Sink1 = cp.Sink("Sink1", logInflows=True)
Sink2 = cp.Sink("Sink2", logInflows=True)
Sink3 = cp.Sink("Sink3", logInflows=True)

# create the list of compartments
compartmentList = [Inflow1, Inflow2, Stock1, Flow1, Sink1, Sink2, Sink3]

# input into model
model.setCompartments(compartmentList)


### INPUT DATA ############################################################################################################################################################

# some raw data
rawdata_inflow1 = [1000, 0, 0, 0, 0]
rawdata_inflow2 = [500, 500, 500, 500, 500]
CV = 0.5

# for storing distributions
data_inflow1 = []
data_inflow2 = []

periodRange = np.arange(0, 5)

for i in periodRange:

    if rawdata_inflow1[i] == 0:
        data_inflow1.append(np.asarray([0] * RUNS))

    else:
        data_inflow1.append(
            nr.triangular(
                rawdata_inflow1[i] * (1 - CV),
                rawdata_inflow1[i],
                rawdata_inflow1[i] * (1 + CV),
                RUNS,
            )
        )

    if rawdata_inflow2[i] == 0:
        data_inflow2.append(np.asarray([0] * RUNS))
    else:
        data_inflow2.append(
            nr.triangular(
                rawdata_inflow2[i] * (1 - CV),
                rawdata_inflow2[i],
                rawdata_inflow2[i] * (1 + CV),
                RUNS,
            )
        )

# include inflows in model
model.addInflow(
    cp.ExternalListInflow(
        Inflow1, [cp.RandomChoiceInflow(data_inflow1[x]) for x in periodRange]
    )
)
model.addInflow(
    cp.ExternalListInflow(
        Inflow2, [cp.RandomChoiceInflow(data_inflow2[x]) for x in periodRange]
    )
)


### TRANSFER COEFFICIENTS #################################################################################################################################################


Inflow1.transfers = [
    cp.StochasticTransfer(nr.triangular, [0.7, 0.8, 0.9], Stock1, priority=2),
    cp.ConstTransfer(1, Flow1, priority=1),
]

Inflow2.transfers = [
    cp.StochasticTransfer(nr.triangular, [0.4, 0.6, 0.8], Flow1, priority=2),
    cp.ConstTransfer(1, Sink3, priority=1),
]

Flow1.transfers = [
    cp.StochasticTransfer(nr.triangular, [0.4, 0.5, 0.6], Stock1, priority=2),
    cp.ConstTransfer(1, Sink2, priority=1),
]

Stock1.localRelease = cp.ListRelease([0.5, 0.2, 0.2, 0.1])
Stock1.transfers = [cp.ConstTransfer(1, Sink1, priority=1)]

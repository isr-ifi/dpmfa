# -*- coding: utf-8 -*-

### PACKAGE IMPORT AND VARIABLE DEFINITION ################################################################################################################################

# import necessary packages
import numpy as np
import numpy.random as nr

from dpmfa import components as cp
from dpmfa import model

# create model
simpleModel = model.Model("Simple Experiment for Testing")

RUNS = 10

### COMPARTMENT DEFINITION ################################################################################################################################################

inflow1 = cp.FlowCompartment("Inflow1", logInflows=True, logOutflows=True)
inflow2 = cp.FlowCompartment("Inflow2", logInflows=True, logOutflows=True)

stock1 = cp.Stock("Stock1", logInflows=True, logOutflows=True, logImmediateFlows=True)
flow1 = cp.FlowCompartment("Flow1", logInflows=True, logOutflows=True)

sink1 = cp.Sink("Sink1", logInflows=True)
sink2 = cp.Sink("Sink2", logInflows=True)
sink3 = cp.Sink("Sink3", logInflows=True)

# create the list of compartments
compartmentList = [inflow1, inflow2, stock1, flow1, sink1, sink2, sink3]

# input into model
simpleModel.setCompartments(compartmentList)


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
simpleModel.addInflow(
    cp.ExternalListInflow(
        inflow1, [cp.RandomChoiceInflow(data_inflow1[x]) for x in periodRange]
    )
)
simpleModel.addInflow(
    cp.ExternalListInflow(
        inflow2, [cp.RandomChoiceInflow(data_inflow2[x]) for x in periodRange]
    )
)


### TRANSFER COEFFICIENTS #################################################################################################################################################


inflow1.transfers = [
    cp.StochasticTransfer(nr.triangular, [0.7, 0.8, 0.9], stock1, priority=2),
    cp.ConstTransfer(1, flow1, priority=1),
]

inflow2.transfers = [
    cp.StochasticTransfer(nr.triangular, [0.4, 0.6, 0.8], flow1, priority=2),
    cp.ConstTransfer(1, sink3, priority=1),
]

# flow1.transfers = [
#    cp.StochasticTransfer(nr.triangular, [0.4, 0.5, 0.6], stock1, priority=2),
#    cp.ConstTransfer(1, sink2, priority=1),
# ]

flow1.transfers = [
    cp.TimeDependentDistributionTransfer(
        [
            cp.TransferDistribution(nr.triangular, [0.05, 0.1, 0.15]),
            cp.TransferDistribution(nr.triangular, [0.07, 0.15, 0.23]),
            cp.TransferDistribution(nr.triangular, [0.1, 0.2, 0.3]),
            cp.TransferDistribution(nr.triangular, [0.2, 0.4, 0.6]),
            cp.TransferDistribution(nr.triangular, [0.25, 0.5, 0.75]),
        ],
        stock1,
        priority=2,
    ),
    cp.ConstTransfer(1, sink2, priority=1),
]

stock1.localRelease = cp.ListRelease([0.5, 0.2, 0.2, 0.1])
stock1.transfers = [cp.ConstTransfer(1, sink1, priority=1)]

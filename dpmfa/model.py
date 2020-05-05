# -*- coding: utf-8 -*-
"""
Created on Wed Mar 05 11:18:47 2014

@author: Klaus Bornhöft

Modified by Sana Rajkovic, Véronique Adam, Joao Gonçalves, Qie Qu and Delphine Kawecki

The Model module contains the class model to define simulation models for
dynamic probabilistic material flow modeling and simulation.

The type model aggregates several elements from the components module to a
complete unit that covers all aspects of the original system that are necessary
to comprehend the material flows that lead to a specific accumulation and the
uncertainty about it.
"""

from . import components as cp
import numpy.random as nr


class Model(object):
    """The Model represents the original system as a set of Compartment, flows
    as relative dependencies between the copmartments and absolute, periodic
    inflows to the system.
    The compartment list may contain FlowCompartmentartments that represent immediate
    onflow of material entering a compartment, Sinks that account material
    accumulation over time and Stocks that relese accumulated material after
    some time.

    A PMFA model is assabled using and parametrizing types from the components
    module.


    Parameters:
    ---------------------
    name: string
        the model name
    compartments[]: list<components.Compartment>
        list of all model compartments - Flow Compartments, Stocks and Sinks
    inflows[]: list<components.ExternalInflow>
        list of sources of external inflows to the system
    seed: float
        the seed value for all proability distributions
    """

    def __init__(self, name, compartments=[], inflows=[]):
        self.name = name

        if all(isinstance(comp, cp.Compartment) for comp in compartments):
            self.compartments = compartments
        else:
            print("Error: all compartments are not 'Compartment' instances")

        if all(isinstance(inflow, cp.ExternalInflow) for inflow in inflows):
            self.inflows = inflows
        else:
            print("Error: all inflows are not 'ExternalInflow' instances")

        self.seed = 1
        self.categoriesList = []

    def setCompartments(self, compartmentList):
        """
        Assigns a list of Compartments to the Model

        Parameter:
        ----------------
        compartmentList: list<component.Compartment>
            list of all compartments - Flow Compartments, Sinks and Stocks of \
            the model
        """
        if len([comp.name for comp in compartmentList]) != len(
            set([comp.name for comp in compartmentList])
        ):
            print("Error: all compartment names are not unique")

        if all(isinstance(comp, cp.Compartment) for comp in compartmentList):
            self.compartments = compartmentList
        else:
            print("Error: all compartments are not 'Compartment' instances")

    def addCompartment(self, compartment):
        """
        Adds a single compartment to the model


        Parameters:
        ----------------
        compartment: component.Compartment
        """

        if compartment.name in [comp.name for comp in self.compartments]:
            print("Error: all compartment names are not unique")

        if isinstance(compartment, cp.Compartment):
            self.compartments.append(compartment)
        else:
            print("Error: use the 'Compartment' class")

    def setInflows(self, inflowList):
        """
        Assigns inflow list to the model

        Parameters:
        ----------------
        inflowList: list<components.ExternalInflow>
            list of sources of external inflows to the system
        """
        if all(isinstance(inflow, cp.ExternalInflow) for inflow in inflowList):
            self.inflows = inflowList
        else:
            print("Error: all inflows are not 'ExternalInflow' instances")

    def addInflow(self, inflow):
        """
        Adds an external inflow source to the model

        Parameter:
        ----------------
        inflow: components.ExternalInflow
            an external source
        """
        # OPEN QUESTION: can there be more than one inflow per comp?
        # if not, test here to avoid errors later on
        if isinstance(inflow, cp.ExternalInflow):
            self.inflows.append(inflow)
        else:
            print("Error: use the 'ExternalInflow' class")

    def updateCompartmentCategories(self):
        """
        updates the category list of the model to contain all compartments
        categories
        """
        newCatList = []
        for comp in self.compartments:
            newCatList += comp.categories
        self.categoriesList = list(set(newCatList))

    def getCategoriesList(self):
        return self.categoriesList

    def setSeed(self, seed):
        """
        sets common seed value for all probability distributions of the Model

        Parameter:
        ----------------
        seed: int
            the seed value
        """
        if not isinstance(seed, int):
            print("Error: 'seed' needs to be an int")
        self.seed = seed
        nr.seed(seed)

    def addTransfer(self, compartmentName, transfer):
        """
        Adds a transfer to one Compartment that is part of the model.
        The compartment is accessed by its name.

        Parameters:
        ----------------
        compartmentName: string
            name of the compartment
        transfer: component.Transfer
            transfer to be added
        """
        if isinstance(transfer, cp.Transfer):
            if compartmentName in [comp.name for comp in self.compartments]:
                compartment = next(
                    (
                        comp
                        for comp in self.compartments
                        if comp.name == compartmentName
                    ),
                    None,
                )
                compartment.transfers.append(transfer)
            else:
                print("Error: Compartment is not in compartment list")
        else:
            print("Error: use the 'Transfer' class")

    def setReleaseStrategy(self, stockName, releaseStrategy):
        """
        Defines the release strategy for one Stock that is part of the model.
        The stock is accessed by its name.

        Parameters:
        ----------------
        stockName: string
            name of the stock
        releaseStrategy: components.LocalRelease
            the release strategy

        """
        if isinstance(releaseStrategy, cp.LocalRelease):
            print("Error: the releaseStrategy is not a 'LocalRelease'.")

        stock = next(
            (comp for comp in self.compartments if comp.name == stockName), None
        )

        if stock != None:
            stock.releaseStrategy = releaseStrategy
        else:
            print("Error: there is no such stock: " + str(stockName))

    def checkModelValidity(self):
        """
        Checks the types of the model components; Checks types, if there are
        compartments, if flow compartments have transfers and if stocks have
        a release strategy.
        """
        # test compartments, their transfers and releases
        for comp in self.compartments:

            # test flow compartments
            if isinstance(comp, cp.FlowCompartment):
                transferList = comp.transfers
                if not transferList:
                    print("Error: no transfers assigned to " + str(comp.name))

                for trans in transferList:
                    if not isinstance(trans, cp.Transfer):
                        print(
                            "Error: invalid transfer from "
                            + str(comp.name)
                            + ". Please implement using the class 'Transfer' from 'components'."
                        )

            # test stocks (no need to test transfers, stocks are also FlowCompartments)
            if isinstance(comp, cp.Stock):

                release = comp.localRelease
                if not isinstance(release, cp.LocalRelease):
                    print(
                        "Error: local release from stock "
                        + str(comp.name)
                        + " not assigned or release not assigned using 'LocalRelease'."
                    )

        # test inflows
        if not self.inflows:
            print("Error: No model inflow defined")

    def debugModel(self):
        """
        Prints out a summary of the existing transfers in the model.
        """
        print("")
        print("-----------------------")
        print("Printing out current model content.")
        print(
            "If running debugModel fails, there is an error in the model set-up. Try running checkModelValidity for diagnostics."
        )
        print("-----------------------")

        for comp in self.compartments:

            if isinstance(comp, cp.Stock):
                print("\n" + str(comp.name) + " is a Stock compartment.")

            elif isinstance(comp, cp.FlowCompartment):
                print("\n" + str(comp.name) + " is a Flow compartment.")

            elif isinstance(comp, cp.Sink):
                print("\n" + str(comp.name) + " is a Sink compartment.")

            if isinstance(comp, cp.Stock) or isinstance(comp, cp.FlowCompartment):
                for trans in comp.transfers:
                    print("--> " + str(trans.target.name) + ": ", end="")

                    if isinstance(trans, cp.Transfer):

                        if isinstance(trans, cp.ConstTransfer):
                            print(
                                "ConstTransfer (value:"
                                + str(trans.value)
                                + ", priority: "
                                + str(trans.priority)
                                + ")"
                            )

                        elif isinstance(trans, cp.StochasticTransfer):
                            print(
                                "StochasticTransfer (function:"
                                + str(trans.function)
                                + ", parameters: "
                                + str(trans.parameters)
                                + ", priority: "
                                + str(trans.priority)
                                + ")"
                            )

                        elif isinstance(trans, cp.TimeDependentDistributionTransfer):
                            print(
                                "TimeDependentDistributionTransfer (list length:"
                                + str(len(trans.transfer_distribution_list))
                                + ", priority: "
                                + str(trans.priority)
                                + ")"
                            )

                        elif isinstance(trans, cp.TimeDependentListTransfer):
                            print(
                                "TimeDependentListTransfer (list length:"
                                + str(len(trans.transfer_list))
                                + ", priority: "
                                + str(trans.priority)
                                + ")"
                            )

                        elif isinstance(trans, cp.RandomChoiceTransfer):
                            print(
                                "RandomChoiceTransfer (sample length:"
                                + str(len(trans.sample))
                                + ", priority: "
                                + str(trans.priority)
                                + ")"
                            )

                        elif isinstance(trans, cp.AggregatedTransfer):
                            print(
                                "AggregatedTransfer (priority: "
                                + str(trans.priority)
                                + ")"
                            )

                    else:
                        print(" Error: is not a 'Transfer'!")

        print("-----------------------")
        print("")

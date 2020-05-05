# -*- coding: utf-8 -*-
"""
Created on Wed Feb 12 14:56:22 2014

@author: Klaus Bornhöft

Modified by Sana Rajkovic, Véronique Adam, Joao Gonçalves, Qie Qu and Delphine Kawecki

The components module contains model elements that are necessary to implement a
Probabilistic Material Flow Model. To represent the system, the model elements
need to be parametrized to fit the specific system behavior.

"""

import numpy as np
from functools import reduce

TYPECHECKING = True


class Compartment(object):
    """ A compartment is a distinct area of the investigated system.
    Depending on the scientific question to be aswered with the model a
    compartment can be an environmental media, a geographic region or a logical
    partition in the fate of a material.

    To use a Compartment, please instantiate its subclasses FlowComp, Sink, and
    Stock.
    """

    def __init__(self, name, logInflows, categories):
        self.compNumber = "not defined"  # used in simulator
        self.name = name
        self.logInflows = logInflows
        self.categories = categories

    """
    inits a matrix to log the material inflows for all simulation runs and
    periods
    """

    def initFlowLog(self, runs, periods):
        """
        if flow record is set, a matrix is initialized to log all flows to the
        compartment
        """
        if TYPECHECKING:
            if not isinstance(runs, int):
                raise TypeError("runs must be set to an integer")
            if not isinstance(periods, int):
                raise TypeError("int must be set to an integer")
        if self.logInflows:
            self.inflowRecord = np.zeros((runs, periods))

    def logFlow(self, run, period, amt):
        """
        logs the inflow to the compartment
        """
        if TYPECHECKING:
            if not isinstance(run, int):
                raise TypeError("runs must be set to an integer")
            if not isinstance(period, int):
                raise TypeError("period must be set to an integer")
        # OPEN QUESTION: how should amt be tested? numerical?
        if self.logInflows:
            self.inflowRecord[run, period] = amt


class FlowCompartment(Compartment):
    """ A FlowComp represents a system Compartment without residence time of
    observed material. The further transfer of material to subsequent
    compartments is defined using Transfer objects.

    Parameters:
    ----------------
    name: string
        compartment name
    transfers: list<components.compartment>
        all outgoing transfers from the Flow Compartment
    logInflows: Boolean
        defines if incoming flows are logged for later evaluation
    logOutflows: Boolean
        defines if outgoing flows are logged for later evaluation
    categories: list
        defined a list of categories the stock is part of (for later evaluation)
    """

    def __init__(
        self,
        name,
        transfers=[],
        logInflows=False,
        logOutflows=False,
        adjustOutgoingTCs=True,
        categories=[],
    ):
        if TYPECHECKING:
            if not isinstance(name, str):
                raise TypeError("name must be set to a string")
            if not isinstance(transfers, list):
                raise TypeError("transfers must be set to a list of Transfers")
            if not isinstance(logInflows, bool):
                raise TypeError("logInflows must be set to a boolean")
            if not isinstance(logOutflows, bool):
                raise TypeError("logOutflows must be set to a boolean")
            if not isinstance(adjustOutgoingTCs, bool):
                raise TypeError("adjustOutgoingTCs must be set to a boolean")
            if not isinstance(categories, list) and not isinstance(categories, str):
                raise TypeError("categories must be set to a string or list of strings")

        super(FlowCompartment, self).__init__(name, logInflows, categories)
        self.transfers = transfers
        self.adjustOutTCs = adjustOutgoingTCs
        self.logOutflows = logOutflows
        self.immediateReleaseRate = 1

    def updateTCs(self, period):
        """ used to set current period TCs for time dependent transfers
        """
        for t in self.transfers:
            t.updateTC(period)

        self.adjustTCs()

    def determineTCs(self, useGlobalTCsettings, globalSettingsAdjust):
        """
        Samples transfer from the underlying probability distribution, may \
        adjust to a sum of one over all outgoing transfers.
        """

        for t in self.transfers:
            t.sampleTC()

        if (not useGlobalTCsettings) & self.adjustOutTCs:
            self.adjustTCs()

        elif useGlobalTCsettings & globalSettingsAdjust:
            self.adjustTCs()

    def initFlowLog(self, runs, periods):
        """
        if flow record is set, a matrix is initialized to log all flows to the
        compartment
        if outFlows are logged a dictionary is initialized to log the outflows
        """
        if self.logInflows:
            self.inflowRecord = np.zeros((runs, periods))

        if self.logOutflows:
            self.outflowRecord = {}
            for t in self.transfers:
                self.outflowRecord[t.target.name] = np.zeros((runs, periods))

    def initInventory(self, runs, periods):
        self.inventory = np.zeros((runs, periods))
        self.releaseList = np.zeros((runs, periods))
        self.localRelease.releaseList = np.zeros((runs, periods))

    def logFlow(self, run, period, amt):
        """
        logs the inflow to the compartment
        """
        if self.logInflows:
            self.inflowRecord[run, period] = amt

        if self.logOutflows:
            for t in self.transfers:
                self.outflowRecord[t.target.name][run, period] = t.getCurrentTC() * amt

    def adjustTCs(self):
        """ Adjusts TCs outgoing from one compartment to sum up to one.
        Applies adjustment factor on TCs with the lowest priority first. \
        If that is insufficient (negativ TCs are not allowed), adjustment of \
        the TC with next higher priority and so on...
        """

        tcSum = sum(t.currentTC for t in self.transfers)
        currentPriority = min(t.priority for t in self.transfers)

        while round(tcSum, 6) != 1:

            adjustableTransfers = [
                t for t in self.transfers if t.priority == currentPriority
            ]
            adjustableTCs = [t.currentTC for t in adjustableTransfers]

            currentAdjustSum = sum(adjustableTCs)
            normToValue = max(currentAdjustSum - (tcSum - 1), 0)
            changedTCs = self.__normListSumTo(adjustableTCs, normToValue)

            for i in range(len(changedTCs)):
                adjustableTransfers[i].currentTC = changedTCs[i]

            tcSum = sum(t.currentTC for t in self.transfers)
            tcSum = round(tcSum, 6)
            currentPriority = currentPriority + 1

    def __normListSumTo(self, L, sumTo=1):
        """normalize values of a list to a certain value"""

        sum = reduce(lambda x, y: x + y, L)

        if sum == 0:
            return [0 for x in L]

        return [x / (sum * 1.0) * sumTo for x in L]


class Sink(Compartment):
    """ A model compartment where inflowing material accumulates

    Parameters:
    ----------------
    name: string
        compartment name
    logInflows: Boolean
        defines if incoming flows are logged for later evaluation
    categories: list
        defined a list of categories the stock is part of (for later evaluation)

    """

    def __init__(self, name, logInflows=False, categories=[]):
        if TYPECHECKING:
            if not isinstance(name, str):
                raise TypeError("name must be set to a string")
            if not isinstance(logInflows, bool):
                raise TypeError("logInflows must be set to a boolean")
            if not isinstance(categories, list) and not isinstance(categories, str):
                raise TypeError("categories must be set to a string or list of strings")
        super(Sink, self).__init__(name, logInflows, categories)

    def initInventory(self, runs, periods):
        self.inventory = np.zeros((runs, periods))

    def updateInventory(self, run, period):
        """ transfers the stored amount from the end of a period to the
        beginning of the next one.
        """
        if period != 0:
            self.inventory[run, period] = self.inventory[run, period - 1]

    def storeMaterial(self, run, period, amount):
        """ increases the stored amount by an accumulated inflow"""
        self.inventory[run, period] = self.inventory[run, period] + amount


class Stock(FlowCompartment, Sink):
    """ A Stock is a Sink that releases a part of the stored material in later
    periods.

    Parameters:
    ----------------
    name: string
        compartment name
    transfers: list<components.Transfer>
        transfers of the material released from stock to other compartments
    localRelease: components.LocalRelease
        definition which proportions of the amount of material stored in a \
        period are released in which of the subsequent periods
    logInflows: Boolean
        defines if incoming flows are logged for later evaluation
    logOutflows: Boolean
        defines if outgoing flows are logged for later evaluation
    categories: list
        defined a list of categories the stock is part of (for later evaluation)

    """

    def __init__(
        self,
        name,
        transfers=[],
        localRelease=0,
        logInflows=False,
        logOutflows=False,
        logImmediateFlows=False,
        categories=[],
    ):
        if TYPECHECKING:
            if not isinstance(name, str):
                raise TypeError("name must be set to a string")
            if not isinstance(transfers, list):
                raise TypeError("transfers must be set to a list of Transfers")
            if not isinstance(logInflows, bool):
                raise TypeError("logInflows must be set to a boolean")
            if not isinstance(logOutflows, bool):
                raise TypeError("logOutflows must be set to a boolean")
            if not isinstance(logImmediateFlows, bool):
                raise TypeError("logImmediateFlows must be set to a boolean")
            if not isinstance(categories, list) and not isinstance(categories, str):
                raise TypeError("categories must be set to a string or list of strings")
        super(Stock, self).__init__(
            name, transfers, logInflows, logOutflows, True, categories
        )
        self.localRelease = localRelease
        self.logOutflows = logOutflows
        self.logImmediateFlows = logImmediateFlows
        self.immediateReleaseRate = 1
        self.categories = categories

    def initInventory(self, runs, periods):
        self.inventory = np.zeros((runs, periods))
        self.releaseList = np.zeros((runs, periods))
        self.localRelease.releaseList = np.zeros((runs, periods))
        if self.logImmediateFlows:
            self.immediateFlowRecord = {}
            for t in self.transfers:
                self.immediateFlowRecord[t.target.name] = np.zeros((runs, periods))

    def updateImmediateReleaseRate(self):
        self.immediateReleaseRate = self.localRelease.getImmediateReleaseRate()

    def logFlow(self, run, period, amt):
        """
        logs the inflow to the compartment
        """
        if self.logInflows:
            self.inflowRecord[run, period] = amt

        if self.logOutflows:
            for t in self.transfers:
                self.outflowRecord[t.target.name][run, period] = (
                    self.outflowRecord[t.target.name][run, period]
                    + t.getCurrentTC() * amt * self.immediateReleaseRate
                )

        if self.logImmediateFlows:
            for t in self.transfers:
                self.immediateFlowRecord[t.target.name][run, period] = (
                    t.getCurrentTC() * amt * self.immediateReleaseRate
                )

    def storeMaterial(self, run, period, amount):
        """ stores material and schedules future release according to the
        release strategy of the stock
        """

        self.inventory[run, period] = self.inventory[run, period] + amount * (
            1 - self.immediateReleaseRate
        )
        self.localRelease.scheduleFutureRelease(run, period, amount)

    def releaseMaterial(self, run, period):
        """ takes the release scheduled for the current period distributes it
        to the different target Compartments

        ------------
        returns: Dict {Compartment: amt}
        """
        releaseAmt = self.localRelease.releaseList[run, period]
        self.inventory[run, period] = self.inventory[run, period] - releaseAmt
        releases = {}
        for trans in self.transfers:
            releases[trans.target] = trans.getCurrentTC() * releaseAmt
            if self.logOutflows:
                self.outflowRecord[trans.target.name][run, period] = releases[
                    trans.target
                ]

        return releases


class LocalRelease(object):
    """ Describes after what period how much of the material stored is released
    from stock. To use, implement subclasses.
    """

    def __init__(self):
        self.releaseList = 0

    def getImmediateReleaseRate(self):
        return self.releaseRatesList[0]

    def scheduleFutureRelease(self, currentRun, currentPeriod, storedAmt):
        remainder = 1 - self.releaseRatesList[0]
        per = currentPeriod + 1
        i = 1
        while per < len(self.releaseList[currentRun]) and i < len(
            self.releaseRatesList
        ):
            self.releaseList[currentRun, per] = self.releaseList[
                currentRun, per
            ] + storedAmt * min(self.releaseRatesList[i], remainder)
            remainder = remainder - min(self.releaseRatesList[i], remainder)
            i += 1
            per += 1


class FixedRateRelease(LocalRelease):
    """ A material release plan with constant rate after a delay period. \
    Values are rounded to full periods.

    Parameters:
    ----------------
    releaseRate: float
        periodic release rate
    delay: Integer
        delay time in periods, befor the release starts.

    """

    def __init__(self, releaseRate=1, delay=0):
        super(FixedRateRelease, self).__init__()
        self.releaseRatesList = []
        remainder = 1

        while remainder > 0:
            if releaseRate < remainder:
                self.releaseRatesList.append(releaseRate)
            else:
                self.releaseRatesList.append(remainder)
            remainder = remainder - releaseRate
        delayArray = np.zeros(delay)
        self.releaseRatesList = np.concatenate((delayArray, self.releaseRatesList))


class ListRelease(LocalRelease):
    """ A material release plan with a defined list of partial release rates
    after a delay period

    Parameters:
    ----------------
    releaseRatesList: list<float>
        list of release rates of a stored material in future periods.
    delay: Integer
        delay time in periods, befor the release starts.

    """

    def __init__(self, releaseRatesList=[1], delay=0):
        super(ListRelease, self).__init__()
        delayArray = np.zeros(delay)

        self.releaseRatesList = np.concatenate((delayArray, releaseRatesList))


class FunctionRelease(LocalRelease):
    """ A material release plan based on a distribution function that returns\
    a release rate for every period. The time instant of the relese is\
    relative to the time of material storage in the stock.

    Parameters:
    ----------------
    releaseFunction: function
        function that return the relative release rate for a period
    delay: Integer
        delay time in periods, befor the release starts.
    """

    def __init__(self, releaseFunction, delay=0):
        super(FunctionRelease, self).__init__()
        self.releaseRatesList = []
        self.totRelease = 0
        self.currentPeriod = 0
        self.lastNonZero = 0

        delayArray = np.zeros(delay)

        while (
            self.totRelease < 1 and self.currentPeriod < 500
        ):  # MAX period if no total release
            currentRelease = releaseFunction(self.currentPeriod)
            self.releaseRatesList.append(currentRelease)
            if currentRelease != 0:
                self.lastNonZero = self.currentPeriod
            self.totRelease += currentRelease
            self.currentPeriod += 1

        if self.currentPeriod - 1 != self.lastNonZero:
            self.releaseRatesList = self.releaseRatesList[: self.lastNonZero + 1]

        if self.totRelease > 1:
            self.releaseRatesList[-1] += 1 - self.totRelease
        self.releaseList = np.concatenate((delayArray, self.releaseRatesList))


class Transfer(object):
    """ A transfer object determines the relative rate of a total material flow
    that is transfered from one Compartment to another. The priority denotes
    the relative credibility of the assumed values and can be used for the
    adjustment of contradictory dependent TCs.

    To implement, use subclass.
    """

    def __init__(self, target, priority):
        self.target = target
        self.priority = priority
        self.currentTC = 0

    def sampleTC(self):
        print("To be implemented in Subclass")

    def getCurrentTC(self):
        return self.currentTC

    """ To be overwritten by time dependent transfers"""

    def updateTC(self, period):
        pass


class ConstTransfer(Transfer):
    """ A Transfer with a deterministic TC.

    Parameters:
    ----------------
    value: float
        determinstic value for the transfer coefficient
    target: components.Compartment
        specifies the target compartment of the transfer
    priority: integer
        if the sum of the transfer coefficients from a compartment are normalized, \
        a higher priority excludes the value from adjustment

    """

    def __init__(self, value, target, priority=1):
        if TYPECHECKING:
            if not isinstance(value, float) and not isinstance(value, int):
                raise TypeError("value must be set to a number")
            if not isinstance(target, Compartment):
                raise TypeError("target must be set to a compartment")
            if not isinstance(priority, int):
                raise TypeError("priority must be set to an integer")
        super(ConstTransfer, self).__init__(target, priority)
        self.value = value
        self.currentTC = value

    def sampleTC(self):
        """ assign the constant value as current TC """
        self.currentTC = self.value


class StochasticTransfer(Transfer):
    """ A Transfer Coefficient determined by an underlying probability \
    distribution

    Parameters:
    ----------------
    function: probability density function
        probability distribution function (e.g. from scipy.stats) to sample \
        random values for the transfer coefficient
    parameters: list<float>
        parameter list of the probability distribution function
    target: components.Compartment
        specifies the target compartment of the transfer
    priority: integer
        if the sum of the transfer coefficients from a compartment are normalized, \
        a higher priority excludes the value from adjustment

    """

    def __init__(self, function, parameters, target, priority=1):
        if TYPECHECKING:
            # OPEN QUESTION: how should the function and parameters be tested?
            if not isinstance(target, Compartment):
                raise TypeError("target must be set to a compartment")
            if not isinstance(priority, int):
                raise TypeError("priority must be set to an integer")
        super(StochasticTransfer, self).__init__(target, priority)
        self.function = function
        self.parameters = parameters

    def sampleTC(self):
        """ samples a random value from the probability distribution as current
        TC
        """
        self.currentTC = self.function(*self.parameters)


############################### Time 'dependent' classes ########################


class TransferDistribution:
    """ A Transfer Coefficient determined by an underlying probability \
    distribution. Only to be used with TimeDependentDistributionTransfer

    Parameters:
    ----------------
    function: probability density function
        probability distribution function (e.g. from scipy.stats) to sample \
        random values for the transfer coefficient
    parameters: list<float>
        parameter list of the probability distribution function

    """

    def __init__(self, function, parameters):
        # OPEN QUESTION: how should the function and parameters be tested?
        self.function = function
        self.parameters = parameters

    def sampleTC(self):
        """ samples a random value from the probability distribution as current
        TC
        """
        return self.function(*self.parameters)


class TransferConstant:
    """ A Transfer with a deterministic TC. To be used within
        TimeDependentDistributionTransfer.
    Parameters:
    ----------------
    value: float
        determinstic value for the transfer coefficient
    """

    def __init__(self, value):
        if TYPECHECKING:
            if not isinstance(value, float) and not isinstance(value, int):
                raise TypeError("value must be set to a number")
        self.value = value

    def sampleTC(self):
        """ assign the constant value as current TC """
        return self.value


class TimeDependentDistributionTransfer(Transfer):
    """ A Transfer Coefficient determined by a given sample.

        Parameters:
        ----------------
        transfer_distribution_list: list<component.TransferDistributions>
            list of TransferDistributions for each period
        sample: list<float>
            a given sample of values from which is randomly drawn
        target: components.Compartment
            specifies the target compartment of the transfer
        priority: integer
            if random values for the transfer coefficients are normalized, \
            a higher priority excludes the value from adjustment
    """

    def __init__(self, transfer_distribution_list, target, owning_comp, priority=1):
        if TYPECHECKING:
            if not isinstance(transfer_distribution_list, list):
                raise TypeError("transfer_distribution_list must be set to a list")
            if not isinstance(target, Compartment):
                raise TypeError("target must be set to a compartment")
            if not isinstance(owning_comp, Compartment):
                raise TypeError("owning_comp must be set to a compartment")
            if not isinstance(priority, int):
                raise TypeError("priority must be set to an integer")
        super(TimeDependentDistributionTransfer, self).__init__(target, priority)
        self.transfer_distribution_list = transfer_distribution_list
        self.transfer_list = []
        self.owning_comp = owning_comp

    def sampleTC(self):
        self.transfer_list = []
        """ Randomly assigns one value from the sample as current TC"""

        for d in self.transfer_distribution_list:
            self.transfer_list.append(
                d.sampleTC()
            )  # creates a list of sampeled values which will be attributed to each period

    def updateTC(self, period):
        self.currentTC = self.transfer_list[period]


class TimeDependentListTransfer(Transfer):
    """ A Transfer Coefficient determined by a given sample.

        Parameters:
        ----------------
        sample: list<float>
            a given sample of values from which is randomly drawn
        transfer_list: list<PeriodTransfer>
            list of Single transfer elements for each period
        target: components.Compartment
            specifies the target compartment of the transfer
        owning_comp: components.Compartment
            specifies from which compartment the transfer comes from
        priority: integer
            if random values for the transfer coefficients are normalized, \
            a higher priority excludes the value from adjustment

    """

    def __init__(self, transfer_list, target, owning_comp, priority=1):
        if TYPECHECKING:
            if not isinstance(transfer_list, list):
                raise TypeError(
                    "transfer_list must be set to a list of Transfer elements"
                )
            if not isinstance(target, Compartment):
                raise TypeError("target must be set to a compartment")
            if not isinstance(owning_comp, Compartment):
                raise TypeError("owning_comp must be set to a compartment")
            if not isinstance(priority, int):
                raise TypeError("priority must be set to an integer")
        super(TimeDependentListTransfer, self).__init__(target, priority)
        self.transfer_list = transfer_list
        self.owning_comp = owning_comp

    def sampleTC(self):
        """ Randomly assigns one value from the sample as current TC"""

    def updateTC(self, period):
        self.currentTC = self.transfer_list[period]


###########################################################################################


class RandomChoiceTransfer(Transfer):
    """ A Transfer Coefficient determined by a given sample.

        Parameters:
        ----------------
        sample: list<float>
            a given sample of values from which is randomly drawn
        target: components.Compartment
            specifies the target compartment of the transfer
        priority: integer
            if random values for the transfer coefficients are normalized, \
            a higher priority excludes the value from adjustment

    """

    def __init__(self, sample, target, priority=1):
        if TYPECHECKING:
            if not isinstance(sample, list):
                raise TypeError("sample must be set to a list of values")
            if not isinstance(target, Compartment):
                raise TypeError("target must be set to a compartment")
            if not isinstance(priority, int):
                raise TypeError("priority must be set to an integer")
        super(RandomChoiceTransfer, self).__init__(target, priority)
        self.sample = sample

    def sampleTC(self):
        """ Randomly assigns one value from the sample as current TC"""
        self.currentTC = np.random.choice(self.sample)


class AggregatedTransfer(Transfer):
    """ A Transfer Coefficient from a combined set of several given samples \
    and or probability distributin functions. A weighting factor for the \
    partial samples can be defined.

    Parameters:
    ----------------
    singleTransfers: list<Transfer>
        a list of SochasticTransfers and/or RandomChoiceTransfers to be \
        considered in the combined distribution
    weights: list<float>
        list of weighting factors
    target: components.Compartment
        specifies the target compartment of the transfer
    priority: integer
        if random values for the transfer coefficients are normalized, \
        a higher priority excludes the value from adjustment
    """

    def __init__(self, target, singleTransfers, weights=None, priority=1):
        super(AggregatedTransfer, self).__init__(target, priority)
        self.singleTransfers = singleTransfers
        if weights != None:
            self.weights = weights
        else:
            self.weights = [1] * len(singleTransfers)

    def sampleTC(self):
        cs = np.cumsum(self.weights)  # An array of the weights, cumulatively summed.
        total = sum(self.weights)
        ind = sum(
            cs < np.random.uniform(0, total)
        )  # Find the index of the first weight over a random value.
        transfer = self.singleTransfers[ind]
        transfer.sampleTC()
        self.currentTC = transfer.getCurrentTC()


class SinglePeriodInflow(object):
    """ A single inflow represents the inflow of material to the model in \
    one single period. To implement material inflows to the system over the\
    entire simulated time implement ExternalListInflow or ExternalFunctionInflow

    To implement use subclass

    """

    def __init__(self):
        self.currentValue = None

    def sampleValue(self):
        pass

    def getValue(self):
        return self.currentValue


class StochasticFunctionInflow(SinglePeriodInflow):
    """ External inflow to a compartment of one Period. Uncertainty about\
    the true value of this inflow is represented as probability distribution\
    function.

    Parameters:
    ----------------
    ProbabilityDistribution: probability density function
        probability distribution (e.g. from scipy.stats) to represent uncertain\
        knowledge about the true value of the inflow
    values: list<float>
        parameter list of the distribution function.

    """

    def __init__(self, probabilityDistribution, parameters):
        super(StochasticFunctionInflow, self).__init__()
        self.pdf = probabilityDistribution
        self.parameterValues = parameters

    def sampleValue(self):
        self.currentValue = self.pdf(*self.parameterValues)


class RandomChoiceInflow(SinglePeriodInflow):
    """ External inflow to a compartment in one Period. Uncertatinty about\
    the true value of this inflow is represented as a sample representing the\
    the assumptions about the true value.

    Parameter:
    ----------------
    sample: list<float>
        sample to draw random value from
    """

    def __init__(self, sample):
        super(RandomChoiceInflow, self).__init__()
        self.sample = sample

    def sampleValue(self):
        self.currentValue = np.random.choice(self.sample)


class FixedValueInflow(SinglePeriodInflow):
    """ External inflow amount to a compartment in one Period.

    Parameter:
    ----------------
    value: float
        the inflow vlaue
    """

    def __init__(self, value):
        super(FixedValueInflow, self).__init__()
        self.currentValue = value


class ExternalInflow(object):
    """ Represents the external material inflow to the observed system.

    To implement, please use subclass
    """

    def __init__(
        self, target, derivationDistribution, derivationParameters, startDelay
    ):
        self.target = target
        self.startDelay = startDelay
        self.derivationDistribution = derivationDistribution
        self.derivationParameters = derivationParameters
        self.derivationFactor = 1

    def getCurrentInflow(self, period):
        pass


class ExternalListInflow(ExternalInflow):
    """ Source of external inflows as a list of material amounts for each period \
    considered in the model.

        Parameters:
        ----------------
        target: components.Compartment
            target compartment of the external inflow.
        valueList: list<SingleInflow>
            list of Single Inflow elements for each period
        derivationDistribution: probability density function
            probability distribution (e.g. from scipy.stats) to represent uncertain\
            knowledge about the true value of the model inflows. The derivation \
            is calculated once per simulation rund and applied to the whole inflow list
        derivationParameters: list<float>
            parameter list of the probability distribution function of the \
            derivation
        startDelay: integer
            time lag between the simulation start and the first release from the source.
    """

    def __init__(
        self,
        target,
        inflowList,
        derivationDistribution=None,
        derivationParameters=[],
        startDelay=0,
    ):
        super(ExternalListInflow, self).__init__(
            target, derivationDistribution, derivationParameters, startDelay
        )
        self.inflowList = inflowList

        for i in range(len(self.inflowList)):
            if isinstance(self.inflowList[i], (int, float, list)):
                self.inflowList[i] = StochasticFunctionInflow(self.inflowList[i])

    def getCurrentInflow(self, period=0):
        """ determines the inflow for a given period"""

        if period - self.startDelay < 0:
            return 0
        else:
            if (period - self.startDelay) < len(self.inflowList):
                returnValue = (
                    self.inflowList[(period - self.startDelay)].getValue()
                    * self.derivationFactor
                )
                if returnValue >= 0:
                    return returnValue
                else:
                    return 0
            else:
                return 0

    def sampleValues(self):
        for inf in self.inflowList:
            inf.sampleValue()
        if self.derivationDistribution != None:
            self.derivationFactor = self.derivationDistribution(
                *self.derivationParameters
            )


class ExternalFunctionInflow(ExternalInflow):

    """ External source; mean inflow amounts as function of time, relative \
    derivation from stochastic distribution. delay function.

    Parameters:
    --------------
    target: components.Compartment
        target compartment of the external inflow.
    basicInflow: components.SingleInflow
        initial inflow to the system in the first period
    inflowFunction: function
        returns a material amount as inflow for a specific period; gets basic\
        Value and period number as input. If no input function is defined, the \
        basic value is used for all periods.
    derivationDistribution: probability density function
        probability distribution (e.g. from scipy.stats) to represent uncertain\
        knowledge about the true value of the model inflows. The derivation \
        is calculated once per simulation rund and applied to the whole inflow list
    derivationParameters: list<float>
        parameter list of the probability distribution function of the \
        derivation
    startDelay: integer
        time lag between the simulation start and the first release from the source.

    """

    def __init__(
        self,
        target,
        basicInflow,
        inflowFunction=None,
        defaultInflowFunction=0,
        derivationDistribution=None,
        derivationParameters=[],
        startDelay=0,
    ):
        super(ExternalFunctionInflow, self).__init__(
            target, derivationDistribution, derivationParameters, startDelay
        )
        if inflowFunction == None:
            self.inflowFunction = self.defaultInflowFunction
        else:
            self.inflowFunction = inflowFunction

        #!port long doesn't exist in python 3
        if isinstance(basicInflow, (int, float, list)):
            self.basicInflow = SinglePeriodInflow(basicInflow)
        else:
            self.basicInflow = basicInflow

    def getCurrentInflow(self, period=0):
        if period - self.startDelay < 0:
            return 0
        else:
            returnValue = (
                self.inflowFunction(self.baseValue, period - self.startDelay)
                * self.derivationFactor
            )
            if returnValue >= 0:
                return returnValue
            else:
                return 0

    def sampleValues(self):
        self.basicInflow.sampleValue()
        self.baseValue = self.basicInflow.getValue()
        if self.derivationDistribution != None:
            self.derivationFactor = self.derivationDistribution(
                *self.derivationParameters
            )

    def defaultInflowFunction(self, base, period):
        return base

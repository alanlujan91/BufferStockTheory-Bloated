"""
This file contains classes and functions for representing, solving, and simulating
agents who must allocate their resources among consumption, saving in a risk-free
asset (with a low return), and saving in a risky asset (with higher average return).
"""
from copy import deepcopy

import numpy as np
from scipy.optimize import minimize_scalar
from HARK import MetricObject, NullFunc, AgentType  # Basic HARK features
from HARK.ConsumptionSaving.ConsIndShockModel import (
    IndShockConsumerType,  # PortfolioConsumerType inherits from it
    utility,  # CRRA utility function
    utility_inv,  # Inverse CRRA utility function
    utilityP,  # CRRA marginal utility function
    utility_invP,  # Derivative of inverse CRRA utility function
    utilityP_inv,  # Inverse CRRA marginal utility function
    init_idiosyncratic_shocks,  # Baseline dictionary to build on
)
from HARK.ConsumptionSaving.ConsRiskyAssetModel import RiskyAssetConsumerType
from HARK.distribution import calc_expectation
from HARK.interpolation import (
    LinearInterp,  # Piecewise linear interpolation
    CubicInterp,  # Piecewise cubic interpolation
    LinearInterpOnInterp1D,  # Interpolator over 1D interpolations
    BilinearInterp,  # 2D interpolator
    ConstantFunction,  # Interpolator-like class that returns constant value
    IdentityFunction,  # Interpolator-like class that returns one of its arguments
    ValueFuncCRRA,
    MargValueFuncCRRA,
)


# Define a class to represent the single period solution of the portfolio choice problem
class PortfolioSolution(MetricObject):
    """
    A class for representing the single period solution of the portfolio choice model.

    Parameters
    ----------
    cFuncAdj : Interp1D
        Consumption function over normalized market resources when the agent is able
        to adjust their portfolio shares.
    ShareFuncAdj : Interp1D
        Risky share function over normalized market resources when the agent is able
        to adjust their portfolio shares.
    vFuncAdj : ValueFuncCRRA
        Value function over normalized market resources when the agent is able to
        adjust their portfolio shares.
    vPfuncAdj : MargValueFuncCRRA
        Marginal value function over normalized market resources when the agent is able
        to adjust their portfolio shares.
    cFuncFxd : Interp2D
        Consumption function over normalized market resources and risky portfolio share
        when the agent is NOT able to adjust their portfolio shares, so they are fixed.
    ShareFuncFxd : Interp2D
        Risky share function over normalized market resources and risky portfolio share
        when the agent is NOT able to adjust their portfolio shares, so they are fixed.
        This should always be an IdentityFunc, by definition.
    vFuncFxd : ValueFuncCRRA
        Value function over normalized market resources and risky portfolio share when
        the agent is NOT able to adjust their portfolio shares, so they are fixed.
    dvdmFuncFxd : MargValueFuncCRRA
        Marginal value of mNrm function over normalized market resources and risky
        portfolio share when the agent is NOT able to adjust their portfolio shares,
        so they are fixed.
    dvdsFuncFxd : MargValueFuncCRRA
        Marginal value of Share function over normalized market resources and risky
        portfolio share when the agent is NOT able to adjust their portfolio shares,
        so they are fixed.
    aGrid: np.array
        End-of-period-assets grid used to find the solution.
    Share_adj: np.array
        Optimal portfolio share associated with each aGrid point.
    EndOfPrddvda_adj: np.array
        Marginal value of end-of-period resources associated with each aGrid
        point.
    ShareGrid: np.array
        Grid for the portfolio share that is used to solve the model.
    EndOfPrddvda_fxd: np.array
        Marginal value of end-of-period resources associated with each
        (aGrid x sharegrid) combination, for the agent who can not adjust his
        portfolio.
    AdjustPrb: float
        Probability that the agent will be able to adjust his portfolio
        next period.
    """

    distance_criteria = ["vPfuncAdj"]

    def __init__(
        self,
        cFuncAdj=None,
        ShareFuncAdj=None,
        vFuncAdj=None,
        vPfuncAdj=None,
        cFuncFxd=None,
        ShareFuncFxd=None,
        vFuncFxd=None,
        dvdmFuncFxd=None,
        dvdsFuncFxd=None,
        aGrid=None,
        Share_adj=None,
        EndOfPrddvda_adj=None,
        ShareGrid=None,
        EndOfPrddvda_fxd=None,
        AdjPrb=None,
    ):

        # Change any missing function inputs to NullFunc
        if cFuncAdj is None:
            cFuncAdj = NullFunc()
        if cFuncFxd is None:
            cFuncFxd = NullFunc()
        if ShareFuncAdj is None:
            ShareFuncAdj = NullFunc()
        if ShareFuncFxd is None:
            ShareFuncFxd = NullFunc()
        if vFuncAdj is None:
            vFuncAdj = NullFunc()
        if vFuncFxd is None:
            vFuncFxd = NullFunc()
        if vPfuncAdj is None:
            vPfuncAdj = NullFunc()
        if dvdmFuncFxd is None:
            dvdmFuncFxd = NullFunc()
        if dvdsFuncFxd is None:
            dvdsFuncFxd = NullFunc()

        # Set attributes of self
        self.cFuncAdj = cFuncAdj
        self.cFuncFxd = cFuncFxd
        self.ShareFuncAdj = ShareFuncAdj
        self.ShareFuncFxd = ShareFuncFxd
        self.vFuncAdj = vFuncAdj
        self.vFuncFxd = vFuncFxd
        self.vPfuncAdj = vPfuncAdj
        self.dvdmFuncFxd = dvdmFuncFxd
        self.dvdsFuncFxd = dvdsFuncFxd
        self.aGrid = aGrid
        self.Share_adj = Share_adj
        self.EndOfPrddvda_adj = EndOfPrddvda_adj
        self.ShareGrid = ShareGrid
        self.EndOfPrddvda_fxd = EndOfPrddvda_fxd
        self.AdjPrb = AdjPrb


class PortfolioConsumerType(RiskyAssetConsumerType):
    """
    A consumer type with a portfolio choice. This agent type has log-normal return
    factors. Their problem is defined by a coefficient of relative risk aversion,
    intertemporal discount factor, risk-free interest factor, and time sequences of
    permanent income growth rate, survival probability, and permanent and transitory
    income shock standard deviations (in logs).  The agent may also invest in a risky
    asset, which has a higher average return than the risk-free asset.  He *might*
    have age-varying beliefs about the risky-return; if he does, then "true" values
    of the risky asset's return distribution must also be specified.
    """

    time_inv_ = deepcopy(RiskyAssetConsumerType.time_inv_)
    time_inv_ = time_inv_ + ["AdjustPrb", "DiscreteShareBool"]

    def __init__(self, verbose=False, quiet=False, **kwds):
        params = init_portfolio.copy()
        params.update(kwds)
        kwds = params

        # Initialize a basic consumer type
        RiskyAssetConsumerType.__init__(
            self, verbose=verbose, quiet=quiet, **kwds
        )

        # Set the solver for the portfolio model, and update various constructed attributes
        self.solve_one_period = solveConsPortfolio
        self.update()

    def pre_solve(self):
        AgentType.pre_solve(self)
        self.update_solution_terminal()

    def update(self):

        RiskyAssetConsumerType.update(self)
        self.update_ShareGrid()
        self.update_ShareLimit()

    def update_solution_terminal(self):
        """
        Solves the terminal period of the portfolio choice problem.  The solution is
        trivial, as usual: consume all market resources, and put nothing in the risky
        asset (because you have nothing anyway).

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Consume all market resources: c_T = m_T
        cFuncAdj_terminal = IdentityFunction()
        cFuncFxd_terminal = IdentityFunction(i_dim=0, n_dims=2)

        # Risky share is irrelevant-- no end-of-period assets; set to zero
        ShareFuncAdj_terminal = ConstantFunction(0.0)
        ShareFuncFxd_terminal = IdentityFunction(i_dim=1, n_dims=2)

        # Value function is simply utility from consuming market resources
        vFuncAdj_terminal = ValueFuncCRRA(cFuncAdj_terminal, self.CRRA)
        vFuncFxd_terminal = ValueFuncCRRA(cFuncFxd_terminal, self.CRRA)

        # Marginal value of market resources is marg utility at the consumption function
        vPfuncAdj_terminal = MargValueFuncCRRA(cFuncAdj_terminal, self.CRRA)
        dvdmFuncFxd_terminal = MargValueFuncCRRA(cFuncFxd_terminal, self.CRRA)
        dvdsFuncFxd_terminal = ConstantFunction(
            0.0
        )  # No future, no marg value of Share

        # Construct the terminal period solution
        self.solution_terminal = PortfolioSolution(
            cFuncAdj=cFuncAdj_terminal,
            ShareFuncAdj=ShareFuncAdj_terminal,
            vFuncAdj=vFuncAdj_terminal,
            vPfuncAdj=vPfuncAdj_terminal,
            cFuncFxd=cFuncFxd_terminal,
            ShareFuncFxd=ShareFuncFxd_terminal,
            vFuncFxd=vFuncFxd_terminal,
            dvdmFuncFxd=dvdmFuncFxd_terminal,
            dvdsFuncFxd=dvdsFuncFxd_terminal,
        )

    def update_ShareGrid(self):
        """
        Creates the attribute ShareGrid as an evenly spaced grid on [0.,1.], using
        the primitive parameter ShareCount.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.ShareGrid = np.linspace(0.0, 1.0, self.ShareCount)
        self.add_to_time_inv("ShareGrid")

    def update_ShareLimit(self):
        """
        Creates the attribute ShareLimit, representing the limiting lower bound of
        risky portfolio share as mNrm goes to infinity.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        if "RiskyDstn" in self.time_vary:
            self.ShareLimit = []
            for t in range(self.T_cycle):
                RiskyDstn = self.RiskyDstn[t]
                temp_f = lambda s: -((1.0 - self.CRRA) ** -1) * np.dot(
                    (self.Rfree + s * (RiskyDstn.X - self.Rfree)) ** (1.0 - self.CRRA),
                    RiskyDstn.pmf,
                )
                SharePF = minimize_scalar(temp_f, bounds=(0.0, 1.0), method="bounded").x
                self.ShareLimit.append(SharePF)
            self.add_to_time_vary("ShareLimit")

        else:
            RiskyDstn = self.RiskyDstn
            temp_f = lambda s: -((1.0 - self.CRRA) ** -1) * np.dot(
                (self.Rfree + s * (RiskyDstn.X - self.Rfree)) ** (1.0 - self.CRRA),
                RiskyDstn.pmf,
            )
            SharePF = minimize_scalar(temp_f, bounds=(0.0, 1.0), method="bounded").x
            self.ShareLimit = SharePF
            self.add_to_time_inv("ShareLimit")

    def get_Rfree(self):
        """
        Calculates realized return factor for each agent, using the attributes Rfree,
        RiskyNow, and ShareNow.  This method is a bit of a misnomer, as the return
        factor is not riskless, but would more accurately be labeled as Rport.  However,
        this method makes the portfolio model compatible with its parent class.

        Parameters
        ----------
        None

        Returns
        -------
        Rport : np.array
            Array of size AgentCount with each simulated agent's realized portfolio
            return factor.  Will be used by get_states() to calculate mNrmNow, where it
            will be mislabeled as "Rfree".
        """
        Rport = (
            self.controls["Share"] * self.shocks["Risky"]
            + (1.0 - self.controls["Share"]) * self.Rfree
        )
        self.Rport = Rport
        return Rport

    def initialize_sim(self):
        """
        Initialize the state of simulation attributes.  Simply calls the same method
        for IndShockConsumerType, then sets the type of AdjustNow to bool.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # these need to be set because "post states",
        # but are a control variable and shock, respectively
        self.controls["Share"] = np.zeros(self.AgentCount)
        RiskyAssetConsumerType.initialize_sim(self)

    def sim_birth(self, which_agents):
        """
        Create new agents to replace ones who have recently died; takes draws of
        initial aNrm and pLvl, as in ConsIndShockModel, then sets Share and Adjust
        to zero as initial values.
        Parameters
        ----------
        which_agents : np.array
            Boolean array of size AgentCount indicating which agents should be "born".

        Returns
        -------
        None
        """
        IndShockConsumerType.sim_birth(self, which_agents)

        self.controls["Share"][which_agents] = 0
        # here a shock is being used as a 'post state'
        self.shocks["Adjust"][which_agents] = False

    def get_controls(self):
        """
        Calculates consumption cNrmNow and risky portfolio share ShareNow using
        the policy functions in the attribute solution.  These are stored as attributes.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        cNrmNow = np.zeros(self.AgentCount) + np.nan
        ShareNow = np.zeros(self.AgentCount) + np.nan

        # Loop over each period of the cycle, getting controls separately depending on "age"
        for t in range(self.T_cycle):
            these = t == self.t_cycle

            # Get controls for agents who *can* adjust their portfolio share
            those = np.logical_and(these, self.shocks["Adjust"])
            cNrmNow[those] = self.solution[t].cFuncAdj(self.state_now["mNrm"][those])
            ShareNow[those] = self.solution[t].ShareFuncAdj(
                self.state_now["mNrm"][those]
            )

            # Get Controls for agents who *can't* adjust their portfolio share
            those = np.logical_and(these, np.logical_not(self.shocks["Adjust"]))
            cNrmNow[those] = self.solution[t].cFuncFxd(
                self.state_now["mNrm"][those], ShareNow[those]
            )
            ShareNow[those] = self.solution[t].ShareFuncFxd(
                self.state_now["mNrm"][those], ShareNow[those]
            )

        # Store controls as attributes of self
        self.controls["cNrm"] = cNrmNow
        self.controls["Share"] = ShareNow


# Define a non-object-oriented one period solver
def solveConsPortfolio(
    solution_next,
    ShockDstn,
    IncShkDstn,
    RiskyDstn,
    LivPrb,
    DiscFac,
    CRRA,
    Rfree,
    PermGroFac,
    BoroCnstArt,
    aXtraGrid,
    ShareGrid,
    vFuncBool,
    AdjustPrb,
    DiscreteShareBool,
    ShareLimit,
    IndepDstnBool,
):
    """
    Solve the one period problem for a portfolio-choice consumer.

    Parameters
    ----------
    solution_next : PortfolioSolution
        Solution to next period's problem.
    ShockDstn : [np.array]
        List with four arrays: discrete probabilities, permanent income shocks,
        transitory income shocks, and risky returns.  This is only used if the
        input IndepDstnBool is False, indicating that income and return distributions
        can't be assumed to be independent.
    IncShkDstn : distribution.Distribution
        Discrete distribution of permanent income shocks
        and transitory income shocks.  This is only used if the input IndepDsntBool
        is True, indicating that income and return distributions are independent.
    RiskyDstn : [np.array]
        List with two arrays: discrete probabilities and risky asset returns. This
        is only used if the input IndepDstnBool is True, indicating that income
        and return distributions are independent.
    LivPrb : float
        Survival probability; likelihood of being alive at the beginning of
        the succeeding period.
    DiscFac : float
        Intertemporal discount factor for future utility.
    CRRA : float
        Coefficient of relative risk aversion.
    Rfree : float
        Risk free interest factor on end-of-period assets.
    PermGroFac : float
        Expected permanent income growth factor at the end of this period.
    BoroCnstArt: float or None
        Borrowing constraint for the minimum allowable assets to end the
        period with.  In this model, it is *required* to be zero.
    aXtraGrid: np.array
        Array of "extra" end-of-period asset values-- assets above the
        absolute minimum acceptable level.
    ShareGrid : np.array
        Array of risky portfolio shares on which to define the interpolation
        of the consumption function when Share is fixed.
    vFuncBool: boolean
        An indicator for whether the value function should be computed and
        included in the reported solution.
    AdjustPrb : float
        Probability that the agent will be able to update his portfolio share.
    DiscreteShareBool : bool
        Indicator for whether risky portfolio share should be optimized on the
        continuous [0,1] interval using the FOC (False), or instead only selected
        from the discrete set of values in ShareGrid (True).  If True, then
        vFuncBool must also be True.
    ShareLimit : float
        Limiting lower bound of risky portfolio share as mNrm approaches infinity.
    IndepDstnBool : bool
        Indicator for whether the income and risky return distributions are in-
        dependent of each other, which can speed up the expectations step.

    Returns
    -------
    solution_now : PortfolioSolution
        The solution to the single period consumption-saving with portfolio choice
        problem.  Includes two consumption and risky share functions: one for when
        the agent can adjust his portfolio share (Adj) and when he can't (Fxd).
    """
    # Make sure the individual is liquidity constrained.  Allowing a consumer to
    # borrow *and* invest in an asset with unbounded (negative) returns is a bad mix.
    if BoroCnstArt != 0.0:
        raise ValueError("PortfolioConsumerType must have BoroCnstArt=0.0!")

    # Make sure that if risky portfolio share is optimized only discretely, then
    # the value function is also constructed (else this task would be impossible).
    if DiscreteShareBool and (not vFuncBool):
        raise ValueError(
            "PortfolioConsumerType requires vFuncBool to be True when DiscreteShareBool is True!"
        )

    # Define temporary functions for utility and its derivative and inverse
    u = lambda x: utility(x, CRRA)
    uP = lambda x: utilityP(x, CRRA)
    uPinv = lambda x: utilityP_inv(x, CRRA)
    n = lambda x: utility_inv(x, CRRA)
    nP = lambda x: utility_invP(x, CRRA)

    # Unpack next period's solution
    vPfuncAdj_next = solution_next.vPfuncAdj
    dvdmFuncFxd_next = solution_next.dvdmFuncFxd
    dvdsFuncFxd_next = solution_next.dvdsFuncFxd
    vFuncAdj_next = solution_next.vFuncAdj
    vFuncFxd_next = solution_next.vFuncFxd

    # Major method fork: (in)dependent risky asset return and income distributions
    if IndepDstnBool:  # If the distributions ARE independent...
        # Unpack the shock distribution
        TranShks_next = IncShkDstn.X[1]
        Risky_next = RiskyDstn.X

        # Flag for whether the natural borrowing constraint is zero
        zero_bound = np.min(TranShks_next) == 0.0
        RiskyMax = np.max(Risky_next)

        # bNrm represents R*a, balances after asset return shocks but before income.
        # This just uses the highest risky return as a rough shifter for the aXtraGrid.
        if zero_bound:
            aNrmGrid = aXtraGrid
            bNrmGrid = np.insert(
                RiskyMax * aXtraGrid, 0, np.min(Risky_next) * aXtraGrid[0]
            )
        else:
            # Add an asset point at exactly zero
            aNrmGrid = np.insert(aXtraGrid, 0, 0.0)
            bNrmGrid = RiskyMax * np.insert(aXtraGrid, 0, 0.0)

        # Get grid and shock sizes, for easier indexing
        aNrm_N = aNrmGrid.size
        bNrm_N = bNrmGrid.size
        Share_N = ShareGrid.size

        # Make tiled arrays to calculate future realizations of mNrm and Share when integrating over IncShkDstn
        bNrm_tiled, Share_tiled = np.meshgrid(bNrmGrid, ShareGrid, indexing="ij")

        # Calculate future realizations of market resources
        def m_nrm_next(shocks, b_nrm):
            return b_nrm / (shocks[0] * PermGroFac) + shocks[1]

        # Evaluate realizations of marginal value of market resources next period
        def dvdb_dist(shocks, b_nrm, Share_next):
            mNrm_next = m_nrm_next(shocks, b_nrm)

            dvdmAdj_next = vPfuncAdj_next(mNrm_next)
            if AdjustPrb < 1.0:
                dvdmFxd_next = dvdmFuncFxd_next(mNrm_next, Share_next)
                # Combine by adjustment probability
                dvdm_next = AdjustPrb * dvdmAdj_next + (1.0 - AdjustPrb) * dvdmFxd_next
            else:  # Don't bother evaluating if there's no chance that portfolio share is fixed
                dvdm_next = dvdmAdj_next

            return (shocks[0] * PermGroFac) ** (-CRRA) * dvdm_next

        # Evaluate realizations of marginal value of risky share next period
        def dvds_dist(shocks, b_nrm, Share_next):
            mNrm_next = m_nrm_next(shocks, b_nrm)
            # No marginal value of Share if it's a free choice!
            dvdsAdj_next = np.zeros_like(mNrm_next)
            if AdjustPrb < 1.0:
                dvdsFxd_next = dvdsFuncFxd_next(mNrm_next, Share_next)
                # Combine by adjustment probability
                dvds_next = AdjustPrb * dvdsAdj_next + (1.0 - AdjustPrb) * dvdsFxd_next
            else:  # Don't bother evaluating if there's no chance that portfolio share is fixed
                dvds_next = dvdsAdj_next

            return (shocks[0] * PermGroFac) ** (1.0 - CRRA) * dvds_next

        # If the value function has been requested, evaluate realizations of value
        def v_intermed_dist(shocks, b_nrm, Share_next):
            mNrm_next = m_nrm_next(shocks, b_nrm)

            vAdj_next = vFuncAdj_next(mNrm_next)
            if AdjustPrb < 1.0:
                vFxd_next = vFuncFxd_next(mNrm_next, Share_next)
                # Combine by adjustment probability
                v_next = AdjustPrb * vAdj_next + (1.0 - AdjustPrb) * vFxd_next
            else:  # Don't bother evaluating if there's no chance that portfolio share is fixed
                v_next = vAdj_next

            return (shocks[0] * PermGroFac) ** (1.0 - CRRA) * v_next

        # Calculate intermediate marginal value of bank balances by taking expectations over income shocks
        dvdb_intermed = calc_expectation(IncShkDstn, dvdb_dist, bNrm_tiled, Share_tiled)
        # calc_expectation returns one additional "empty" dimension, remove it
        # this line can be deleted when calc_expectation is fixed
        dvdb_intermed = dvdb_intermed[:, :, 0]
        dvdbNvrs_intermed = uPinv(dvdb_intermed)
        dvdbNvrsFunc_intermed = BilinearInterp(dvdbNvrs_intermed, bNrmGrid, ShareGrid)
        dvdbFunc_intermed = MargValueFuncCRRA(dvdbNvrsFunc_intermed, CRRA)

        # Calculate intermediate value by taking expectations over income shocks
        if vFuncBool:
            v_intermed = calc_expectation(
                IncShkDstn, v_intermed_dist, bNrm_tiled, Share_tiled
            )
            # calc_expectation returns one additional "empty" dimension, remove it
            # this line can be deleted when calc_expectation is fixed
            v_intermed = v_intermed[:, :, 0]
            vNvrs_intermed = n(v_intermed)
            vNvrsFunc_intermed = BilinearInterp(vNvrs_intermed, bNrmGrid, ShareGrid)
            vFunc_intermed = ValueFuncCRRA(vNvrsFunc_intermed, CRRA)

        # Calculate intermediate marginal value of risky portfolio share by taking expectations
        dvds_intermed = calc_expectation(IncShkDstn, dvds_dist, bNrm_tiled, Share_tiled)
        # calc_expectation returns one additional "empty" dimension, remove it
        # this line can be deleted when calc_expectation is fixed
        dvds_intermed = dvds_intermed[:, :, 0]
        dvdsFunc_intermed = BilinearInterp(dvds_intermed, bNrmGrid, ShareGrid)

        # Make tiled arrays to calculate future realizations of bNrm and Share when integrating over RiskyDstn
        aNrm_tiled, Share_tiled = np.meshgrid(aNrmGrid, ShareGrid, indexing="ij")

        # Evaluate realizations of value and marginal value after asset returns are realized

        def EndOfPrddvda_dist(shock, a_nrm, Share_next):
            # Calculate future realizations of bank balances bNrm
            Rxs = shock - Rfree
            Rport = Rfree + Share_next * Rxs
            b_nrm_next = Rport * a_nrm

            return Rport * dvdbFunc_intermed(b_nrm_next, Share_next)

        def EndOfPrdv_dist(shock, a_nrm, Share_next):
            # Calculate future realizations of bank balances bNrm
            Rxs = shock - Rfree
            Rport = Rfree + Share_next * Rxs
            b_nrm_next = Rport * a_nrm

            return vFunc_intermed(b_nrm_next, Share_next)

        def EndOfPrddvds_dist(shock, a_nrm, Share_next):
            # Calculate future realizations of bank balances bNrm
            Rxs = shock - Rfree
            Rport = Rfree + Share_next * Rxs
            b_nrm_next = Rport * a_nrm

            return Rxs * a_nrm * dvdbFunc_intermed(
                b_nrm_next, Share_next
            ) + dvdsFunc_intermed(b_nrm_next, Share_next)

        # Calculate end-of-period marginal value of assets by taking expectations
        EndOfPrddvda = (
            DiscFac
            * LivPrb
            * calc_expectation(RiskyDstn, EndOfPrddvda_dist, aNrm_tiled, Share_tiled)
        )
        # calc_expectation returns one additional "empty" dimension, remove it
        # this line can be deleted when calc_expectation is fixed
        EndOfPrddvda = EndOfPrddvda[:, :, 0]
        EndOfPrddvdaNvrs = uPinv(EndOfPrddvda)

        # Calculate end-of-period value by taking expectations
        if vFuncBool:
            EndOfPrdv = (
                DiscFac
                * LivPrb
                * calc_expectation(RiskyDstn, EndOfPrdv_dist, aNrm_tiled, Share_tiled)
            )
            # calc_expectation returns one additional "empty" dimension, remove it
            # this line can be deleted when calc_expectation is fixed
            EndOfPrdv = EndOfPrdv[:, :, 0]
            EndOfPrdvNvrs = n(EndOfPrdv)

        # Calculate end-of-period marginal value of risky portfolio share by taking expectations
        EndOfPrddvds = (
            DiscFac
            * LivPrb
            * calc_expectation(RiskyDstn, EndOfPrddvds_dist, aNrm_tiled, Share_tiled)
        )
        # calc_expectation returns one additional "empty" dimension, remove it
        # this line can be deleted when calc_expectation is fixed
        EndOfPrddvds = EndOfPrddvds[:, :, 0]

    else:  # If the distributions are NOT independent...
        # Unpack the shock distribution
        ShockPrbs_next = ShockDstn[0]
        PermShks_next = ShockDstn[1]
        TranShks_next = ShockDstn[2]
        Risky_next = ShockDstn[3]
        # Flag for whether the natural borrowing constraint is zero
        zero_bound = np.min(TranShks_next) == 0.0

        # Make tiled arrays to calculate future realizations of mNrm and Share; dimension order: mNrm, Share, shock
        if zero_bound:
            aNrmGrid = aXtraGrid
        else:
            # Add an asset point at exactly zero
            aNrmGrid = np.insert(aXtraGrid, 0, 0.0)

        aNrm_N = aNrmGrid.size
        Share_N = ShareGrid.size
        Shock_N = ShockPrbs_next.size

        aNrm_tiled = np.tile(
            np.reshape(aNrmGrid, (aNrm_N, 1, 1)), (1, Share_N, Shock_N)
        )
        Share_tiled = np.tile(
            np.reshape(ShareGrid, (1, Share_N, 1)), (aNrm_N, 1, Shock_N)
        )
        ShockPrbs_tiled = np.tile(
            np.reshape(ShockPrbs_next, (1, 1, Shock_N)), (aNrm_N, Share_N, 1)
        )
        PermShks_tiled = np.tile(
            np.reshape(PermShks_next, (1, 1, Shock_N)), (aNrm_N, Share_N, 1)
        )
        TranShks_tiled = np.tile(
            np.reshape(TranShks_next, (1, 1, Shock_N)), (aNrm_N, Share_N, 1)
        )
        Risky_tiled = np.tile(
            np.reshape(Risky_next, (1, 1, Shock_N)), (aNrm_N, Share_N, 1)
        )

        # Calculate future realizations of market resources
        Rport = (1.0 - Share_tiled) * Rfree + Share_tiled * Risky_tiled
        mNrm_next = Rport * aNrm_tiled / (PermShks_tiled * PermGroFac) + TranShks_tiled
        Share_next = Share_tiled

        # Evaluate realizations of marginal value of market resources next period
        dvdmAdj_next = vPfuncAdj_next(mNrm_next)
        if AdjustPrb < 1.0:
            dvdmFxd_next = dvdmFuncFxd_next(mNrm_next, Share_next)
            # Combine by adjustment probability
            dvdm_next = AdjustPrb * dvdmAdj_next + (1.0 - AdjustPrb) * dvdmFxd_next
        else:  # Don't bother evaluating if there's no chance that portfolio share is fixed
            dvdm_next = dvdmAdj_next

        # Evaluate realizations of marginal value of risky share next period
        # No marginal value of Share if it's a free choice!
        dvdsAdj_next = np.zeros_like(mNrm_next)
        if AdjustPrb < 1.0:
            dvdsFxd_next = dvdsFuncFxd_next(mNrm_next, Share_next)
            # Combine by adjustment probability
            dvds_next = AdjustPrb * dvdsAdj_next + (1.0 - AdjustPrb) * dvdsFxd_next
        else:  # Don't bother evaluating if there's no chance that portfolio share is fixed
            dvds_next = dvdsAdj_next

        # If the value function has been requested, evaluate realizations of value
        if vFuncBool:
            vAdj_next = vFuncAdj_next(mNrm_next)
            if AdjustPrb < 1.0:
                vFxd_next = vFuncFxd_next(mNrm_next, Share_next)
                v_next = AdjustPrb * vAdj_next + (1.0 - AdjustPrb) * vFxd_next
            else:  # Don't bother evaluating if there's no chance that portfolio share is fixed
                v_next = vAdj_next
        else:
            v_next = np.zeros_like(dvdm_next)  # Trivial array

        # Calculate end-of-period marginal value of assets by taking expectations
        temp_fac_A = uP(PermShks_tiled * PermGroFac)  # Will use this in a couple places
        EndOfPrddvda = (
            DiscFac
            * LivPrb
            * np.sum(ShockPrbs_tiled * Rport * temp_fac_A * dvdm_next, axis=2)
        )
        EndOfPrddvdaNvrs = uPinv(EndOfPrddvda)

        # Calculate end-of-period value by taking expectations
        # Will use this below
        temp_fac_B = (PermShks_tiled * PermGroFac) ** (1.0 - CRRA)
        if vFuncBool:
            EndOfPrdv = (
                DiscFac * LivPrb * np.sum(ShockPrbs_tiled * temp_fac_B * v_next, axis=2)
            )
            EndOfPrdvNvrs = n(EndOfPrdv)

        # Calculate end-of-period marginal value of risky portfolio share by taking expectations
        Rxs = Risky_tiled - Rfree
        EndOfPrddvds = (
            DiscFac
            * LivPrb
            * np.sum(
                ShockPrbs_tiled
                * (Rxs * aNrm_tiled * temp_fac_A * dvdm_next + temp_fac_B * dvds_next),
                axis=2,
            )
        )

    # Major method fork: discrete vs continuous choice of risky portfolio share
    if DiscreteShareBool:  # Optimization of Share on the discrete set ShareGrid
        opt_idx = np.argmax(EndOfPrdv, axis=1)
        Share_now = ShareGrid[opt_idx]  # Best portfolio share is one with highest value
        # Take cNrm at that index as well
        cNrmAdj_now = EndOfPrddvdaNvrs[np.arange(aNrm_N), opt_idx]
        if not zero_bound:
            Share_now[0] = 1.0  # aNrm=0, so there's no way to "optimize" the portfolio
            # Consumption when aNrm=0 does not depend on Share
            cNrmAdj_now[0] = EndOfPrddvdaNvrs[0, -1]

    else:  # Optimization of Share on continuous interval [0,1]
        # For values of aNrm at which the agent wants to put more than 100% into risky asset, constrain them
        FOC_s = EndOfPrddvds
        # Initialize to putting everything in safe asset
        Share_now = np.zeros_like(aNrmGrid)
        cNrmAdj_now = np.zeros_like(aNrmGrid)
        # If agent wants to put more than 100% into risky asset, he is constrained
        constrained_top = FOC_s[:, -1] > 0.0
        # Likewise if he wants to put less than 0% into risky asset
        constrained_bot = FOC_s[:, 0] < 0.0
        Share_now[constrained_top] = 1.0
        if not zero_bound:
            Share_now[0] = 1.0  # aNrm=0, so there's no way to "optimize" the portfolio
            # Consumption when aNrm=0 does not depend on Share
            cNrmAdj_now[0] = EndOfPrddvdaNvrs[0, -1]
            # Mark as constrained so that there is no attempt at optimization
            constrained_top[0] = True

        # Get consumption when share-constrained
        cNrmAdj_now[constrained_top] = EndOfPrddvdaNvrs[constrained_top, -1]
        cNrmAdj_now[constrained_bot] = EndOfPrddvdaNvrs[constrained_bot, 0]
        # For each value of aNrm, find the value of Share such that FOC-Share == 0.
        # This loop can probably be eliminated, but it's such a small step that it won't speed things up much.
        crossing = np.logical_and(FOC_s[:, 1:] <= 0.0, FOC_s[:, :-1] >= 0.0)
        for j in range(aNrm_N):
            if not (constrained_top[j] or constrained_bot[j]):
                idx = np.argwhere(crossing[j, :])[0][0]
                bot_s = ShareGrid[idx]
                top_s = ShareGrid[idx + 1]
                bot_f = FOC_s[j, idx]
                top_f = FOC_s[j, idx + 1]
                bot_c = EndOfPrddvdaNvrs[j, idx]
                top_c = EndOfPrddvdaNvrs[j, idx + 1]
                alpha = 1.0 - top_f / (top_f - bot_f)
                Share_now[j] = (1.0 - alpha) * bot_s + alpha * top_s
                cNrmAdj_now[j] = (1.0 - alpha) * bot_c + alpha * top_c

    # Calculate the endogenous mNrm gridpoints when the agent adjusts his portfolio
    mNrmAdj_now = aNrmGrid + cNrmAdj_now

    # This is a point at which (a,c,share) have consistent length. Take the
    # snapshot for storing the grid and values in the solution.
    save_points = {
        "a": deepcopy(aNrmGrid),
        "eop_dvda_adj": uP(cNrmAdj_now),
        "share_adj": deepcopy(Share_now),
        "share_grid": deepcopy(ShareGrid),
        "eop_dvda_fxd": uP(EndOfPrddvda),
    }

    # Construct the risky share function when the agent can adjust
    if DiscreteShareBool:
        mNrmAdj_mid = (mNrmAdj_now[1:] + mNrmAdj_now[:-1]) / 2
        mNrmAdj_plus = mNrmAdj_mid * (1.0 + 1e-12)
        mNrmAdj_comb = (np.transpose(np.vstack((mNrmAdj_mid, mNrmAdj_plus)))).flatten()
        mNrmAdj_comb = np.append(np.insert(mNrmAdj_comb, 0, 0.0), mNrmAdj_now[-1])
        Share_comb = (np.transpose(np.vstack((Share_now, Share_now)))).flatten()
        ShareFuncAdj_now = LinearInterp(mNrmAdj_comb, Share_comb)
    else:
        if zero_bound:
            Share_lower_bound = ShareLimit
        else:
            Share_lower_bound = 1.0
        Share_now = np.insert(Share_now, 0, Share_lower_bound)
        ShareFuncAdj_now = LinearInterp(
            np.insert(mNrmAdj_now, 0, 0.0),
            Share_now,
            intercept_limit=ShareLimit,
            slope_limit=0.0,
        )

    # Construct the consumption function when the agent can adjust
    cNrmAdj_now = np.insert(cNrmAdj_now, 0, 0.0)
    cFuncAdj_now = LinearInterp(np.insert(mNrmAdj_now, 0, 0.0), cNrmAdj_now)

    # Construct the marginal value (of mNrm) function when the agent can adjust
    vPfuncAdj_now = MargValueFuncCRRA(cFuncAdj_now, CRRA)

    # Construct the consumption function when the agent *can't* adjust the risky share, as well
    # as the marginal value of Share function
    cFuncFxd_by_Share = []
    dvdsFuncFxd_by_Share = []
    for j in range(Share_N):
        cNrmFxd_temp = EndOfPrddvdaNvrs[:, j]
        mNrmFxd_temp = aNrmGrid + cNrmFxd_temp
        cFuncFxd_by_Share.append(
            LinearInterp(
                np.insert(mNrmFxd_temp, 0, 0.0), np.insert(cNrmFxd_temp, 0, 0.0)
            )
        )
        dvdsFuncFxd_by_Share.append(
            LinearInterp(
                np.insert(mNrmFxd_temp, 0, 0.0),
                np.insert(EndOfPrddvds[:, j], 0, EndOfPrddvds[0, j]),
            )
        )
    cFuncFxd_now = LinearInterpOnInterp1D(cFuncFxd_by_Share, ShareGrid)
    dvdsFuncFxd_now = LinearInterpOnInterp1D(dvdsFuncFxd_by_Share, ShareGrid)

    # The share function when the agent can't adjust his portfolio is trivial
    ShareFuncFxd_now = IdentityFunction(i_dim=1, n_dims=2)

    # Construct the marginal value of mNrm function when the agent can't adjust his share
    dvdmFuncFxd_now = MargValueFuncCRRA(cFuncFxd_now, CRRA)

    # If the value function has been requested, construct it now
    if vFuncBool:
        # First, make an end-of-period value function over aNrm and Share
        EndOfPrdvNvrsFunc = BilinearInterp(EndOfPrdvNvrs, aNrmGrid, ShareGrid)
        EndOfPrdvFunc = ValueFuncCRRA(EndOfPrdvNvrsFunc, CRRA)

        # Construct the value function when the agent can adjust his portfolio
        mNrm_temp = aXtraGrid  # Just use aXtraGrid as our grid of mNrm values
        cNrm_temp = cFuncAdj_now(mNrm_temp)
        aNrm_temp = mNrm_temp - cNrm_temp
        Share_temp = ShareFuncAdj_now(mNrm_temp)
        v_temp = u(cNrm_temp) + EndOfPrdvFunc(aNrm_temp, Share_temp)
        vNvrs_temp = n(v_temp)
        vNvrsP_temp = uP(cNrm_temp) * nP(v_temp)
        vNvrsFuncAdj = CubicInterp(
            np.insert(mNrm_temp, 0, 0.0),  # x_list
            np.insert(vNvrs_temp, 0, 0.0),  # f_list
            np.insert(vNvrsP_temp, 0, vNvrsP_temp[0]),  # dfdx_list
        )
        # Re-curve the pseudo-inverse value function
        vFuncAdj_now = ValueFuncCRRA(vNvrsFuncAdj, CRRA)

        # Construct the value function when the agent *can't* adjust his portfolio
        mNrm_temp = np.tile(np.reshape(aXtraGrid, (aXtraGrid.size, 1)), (1, Share_N))
        Share_temp = np.tile(np.reshape(ShareGrid, (1, Share_N)), (aXtraGrid.size, 1))
        cNrm_temp = cFuncFxd_now(mNrm_temp, Share_temp)
        aNrm_temp = mNrm_temp - cNrm_temp
        v_temp = u(cNrm_temp) + EndOfPrdvFunc(aNrm_temp, Share_temp)
        vNvrs_temp = n(v_temp)
        vNvrsP_temp = uP(cNrm_temp) * nP(v_temp)
        vNvrsFuncFxd_by_Share = []
        for j in range(Share_N):
            vNvrsFuncFxd_by_Share.append(
                CubicInterp(
                    np.insert(mNrm_temp[:, 0], 0, 0.0),  # x_list
                    np.insert(vNvrs_temp[:, j], 0, 0.0),  # f_list
                    np.insert(vNvrsP_temp[:, j], 0, vNvrsP_temp[j, 0]),  # dfdx_list
                )
            )
        vNvrsFuncFxd = LinearInterpOnInterp1D(vNvrsFuncFxd_by_Share, ShareGrid)
        vFuncFxd_now = ValueFuncCRRA(vNvrsFuncFxd, CRRA)

    else:  # If vFuncBool is False, fill in dummy values
        vFuncAdj_now = None
        vFuncFxd_now = None

    return PortfolioSolution(
        cFuncAdj=cFuncAdj_now,
        ShareFuncAdj=ShareFuncAdj_now,
        vPfuncAdj=vPfuncAdj_now,
        vFuncAdj=vFuncAdj_now,
        cFuncFxd=cFuncFxd_now,
        ShareFuncFxd=ShareFuncFxd_now,
        dvdmFuncFxd=dvdmFuncFxd_now,
        dvdsFuncFxd=dvdsFuncFxd_now,
        vFuncFxd=vFuncFxd_now,
        aGrid=save_points["a"],
        Share_adj=save_points["share_adj"],
        EndOfPrddvda_adj=save_points["eop_dvda_adj"],
        ShareGrid=save_points["share_grid"],
        EndOfPrddvda_fxd=save_points["eop_dvda_fxd"],
        AdjPrb=AdjustPrb,
    )


# Make a dictionary to specify a portfolio choice consumer type
init_portfolio = init_idiosyncratic_shocks.copy()
init_portfolio["RiskyAvg"] = 1.08  # Average return of the risky asset
init_portfolio["RiskyStd"] = 0.20  # Standard deviation of (log) risky returns
# Number of integration nodes to use in approximation of risky returns
init_portfolio["RiskyCount"] = 5
# Number of discrete points in the risky share approximation
init_portfolio["ShareCount"] = 25
# Probability that the agent can adjust their risky portfolio share each period
init_portfolio["AdjustPrb"] = 1.0
# Flag for whether to optimize risky share on a discrete grid only
init_portfolio["DiscreteShareBool"] = False

# Adjust some of the existing parameters in the dictionary
init_portfolio["aXtraMax"] = 100  # Make the grid of assets go much higher...
init_portfolio["aXtraCount"] = 200  # ...and include many more gridpoints...
init_portfolio["aXtraNestFac"] = 1  # ...which aren't so clustered at the bottom
init_portfolio["BoroCnstArt"] = 0.0  # Artificial borrowing constraint must be turned on
init_portfolio["CRRA"] = 5.0  # Results are more interesting with higher risk aversion
init_portfolio["DiscFac"] = 0.90  # And also lower patience
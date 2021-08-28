# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: ExecuteTime,autoscroll,heading_collapsed,hidden,pycharm,tags,jupyter,-hide_ouput,-code_folding
#     cell_metadata_json: true
#     formats: ipynb,py:percent
#     notebook_metadata_filter: all
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.11.4
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
#   language_info:
#     codemirror_mode:
#       name: ipython
#       version: 3
#     file_extension: .py
#     mimetype: text/x-python
#     name: python
#     nbconvert_exporter: python
#     pygments_lexer: ipython3
#     version: 3.9.6
#   latex_envs:
#     LaTeX_envs_menu_present: true
#     autoclose: false
#     autocomplete: false
#     bibliofile: biblio.bib
#     cite_by: apalike
#     current_citInitial: 1
#     eqLabelWithNumbers: true
#     eqNumInitial: 1
#     hotkeys:
#       equation: Ctrl-E
#       itemize: Ctrl-I
#     labels_anchors: false
#     latex_user_defs: false
#     report_style_numbering: false
#     user_envs_cfg: false
# ---

# %% [markdown]
# # Theoretical Foundations of Buffer Stock Saving -- Interactive Figures
#
# [![econ-ark.org](https://img.shields.io/badge/Powered%20by-Econ--ARK-3e8acc.svg)](https://econ-ark.org/materials/BufferStockTheory)
#
# (Execute the cells below one at a time to activate the corresponding interactive tools)

# %%
# Some setup stuff
from builtins import breakpoint
# Get others' tools
from ipywidgets import interact, interactive, fixed, interact_manual

# Get HARK modeling tool
from HARK.ConsumptionSaving.ConsIndShockModel import IndShockConsumerType

# Get BufferStockTheory dashboard tools
import Dashboard.dashboard_widget as BST

# %% [markdown]
# ## Convergence of the Consumption Rules
#
# Under the given parameter values, [the paper's first figure](http://econ.jhu.edu/people/ccarroll/papers/BufferStockTheory/#Convergence-of-the-Consumption-Rules) depicts the successive consumption rules that apply in the last period of life $(c_{T}(m))$, the second-to-last period, and earlier periods $(c_{T-n})$.  $c(m)$ is the consumption function to which these converge:
#
# $$
# c(m) = \lim_{n \uparrow \infty} c_{T-n}(m)
# $$
#

# %%
# Risk aversion ρ and σ_ψ have the most interesting effects

cFuncsConverge_widget=interactive(
    BST.makeConvergencePlot,
    DiscFac=BST.DiscFac_widget[0],
    CRRA=BST.CRRA_widget[0],
    Rfree=BST.Rfree_widget[0],
    permShkStd=BST.permShkStd_widget[0],
)
cFuncsConverge_widget

# %% [markdown]
# ## [Growth Impatience (Raw and Normalized), and Pseudo-Steady-State versus Target Wealth](http://econ.jhu.edu/people/ccarroll/papers/BufferStockTheory/#The-GIC)
#
# [A figure](http://econ.jhu.edu/people/ccarroll/papers/BufferStockTheory/#FVACnotGIC) in the paper depicts a solution when the **FVAC** [(Finite Value of Autarky Condition)](https://llorracc.github.io/BufferStockTheory/#FVAC) and **WRIC** [(Weak Return Impatience Condition)](https://llorracc.github.io/BufferStockTheory/#WRIC) hold (so that the model has a solution) but the **GIC** [(Growth Impatience Condition)](https://llorracc.github.io/BufferStockTheory/#GIC) fails:
#
# \begin{eqnarray}
# \mathbb{E}\left[\frac{\Phi}{\Gamma\psi}\right] & < & 1
# \end{eqnarray}
#
# (see [Calibrated Parameters](https://llorracc.github.io/BufferStockTheory/#Calibration) and [Definitions and Characteristics Calculated from Parameters](https://llorracc.github.io/BufferStockTheory/#Symbols))
#
# Use the slider to see what happens as you move $\sigma_{\psi}$ from below to above the value that makes the GIC-Nrm condition fail.  
#
# | Param | Description | Code | Value |
# | :---: | ---         | ---  | :---: |
# | $\sigma_{\psi}$ | Std Dev Perm Shk | `permShkStd` | 0.2 |
#
#

# %%
# Make consumer more patient by doubling uncertainty
BST.base_params['permShkStd'] = [2 * 0.1]

# Give solution a bit more precision by increasing density of shocks
BST.base_params['permShkCount'] = BST.permShkCount = 7  #  extra points for accuracy

# Construct an instance, and unquietly describe it
GICNrmFailsButGICRawHolds = \
    IndShockConsumerType(**BST.base_params,
                         quietly=False,
                         messaging_level=10) # level 10 is all messages

# %%
# Under starting parameters, this example has a steady state m but not a target m 
# (the consumption function intersects with the M growth but not the m change locus)
# If permanent shock std is reduced, it will have both steady state m and target m

GICFailsExample_widget = interactive(
    BST.makeGICFailExample,
    DiscFac=BST.DiscFac_widget[1],
    permShkStd=BST.permShkStd_alt_start_widget[1],
    UnempPrb=BST.UnempPrb_widget[1],
)
GICFailsExample_widget


# %% [markdown]
# ### [Balanced Growth "Steady State Equilibrium" $m$, "Target" m, Expected Consumption Growth, and Permanent Income Growth](https://econ.jhu.edu/people/ccarroll/papers/BufferStockTheory/#AnalysisoftheConvergedConsumptionFunction)
#
# The next figure is shown in  [Analysis of the Converged Consumption Function](https://econ.jhu.edu/people/ccarroll/papers/BufferStockTheory/#cGroTargetFig), and depicts the expected consumption growth factor $\mathrm{\mathbb{E}}_{t}[\pmb{\mathrm{c}}_{t+1}/\pmb{\mathrm{c}}_{t}]$ for a consumer behaving according to the converged consumption rule, along with the expected growth factor for market resources $\mathrm{\mathbb{E}}_{t}[\pmb{\mathrm{m}}_{t+1}/\pmb{\mathrm{m}}_{t}]$, and the expected growth factor for the ratio of market resources to permanent income, $\mathrm{\mathbb{E}}_{t}[m_{t+1}/m_{t}]$.
#
# Manipulate the time preference and income growth factors to show the effects on target and pseudo-steady-state ("balanced growth") wealth, whose numerical values appear above the figure.

# %% {"tags": []}
# Explore what happens as you make the consumer more patient in two ways: β ↑ and Γ ↓

BST.base_params['permShkStd'] = [0.1]  #  Restore the original default uncertainty
cGroTargetFig_widget = interactive(
    BST.cGroTargetFig_make,
    PermGroFac=BST.PermGroFac_growth_widget[2],
    DiscFac=BST.DiscFac_growth_widget[2]
)
cGroTargetFig_widget

# %% [markdown]
# ### [Consumption Function Bounds](https://econ.jhu.edu/people/ccarroll/papers/BufferStockTheory/#AnalysisOfTheConvergedConsumptionFunction)
# [The next figure](https://econ.jhu.edu/people/ccarroll/papers/BufferStockTheory/#cFuncBounds)
# illustrates theoretical bounds for the consumption function.
#
# We define two useful variables: lower bound of $\kappa$ (the marginal propensity to consume) and the limit of $h$ (Human wealth), along with some functions such as the limiting perfect foresight consumption function $\bar{c}(m)$, the upper bound function $\bar{\bar c}(m)$, and the lower bound function $\underline{c}(m)$.
#
# Recall that the Perfect Forsight Return Impatience Condition is:
# \begin{eqnarray}
# (R \beta)^{1/\rho} & < & R
# \\ \beta & < & R^{\rho-1}
# \end{eqnarray}
#
# In the figure below, we set $R$ and $\Gamma$ to fixed values of 1.0.  Explore what happens to the consumption function as you move the parameters as far as you can toward the perfect foresight model and the time preference factor up toward 1 (warning: the model takes longer to solve if the RIC is close to failing; be patient).  What would you expect to see if the upper boundary of the figure were extended far enough?  
#
# Notice that the model with uncertainty gets very close to the perfect foresight model only when the uncertainty is tuned down to the very lowest possible levels and the time preference rate is set to a high number.

# %%
cFuncBounds_widget = interactive(
    BST.makeBoundsFigure,
    UnempPrb=BST.UnempPrb_widget[3],
    permShkStd=BST.permShkStd_widget[3],
    TranShkStd=BST.TranShkStd_widget[3],
    DiscFac=BST.DiscFac_widget[3],
    CRRA=BST.CRRA_widget[3]
)
cFuncBounds_widget


# %% [markdown]
# ### [Upper and Lower Limits of the Marginal Propensity to Consume](https://econ.jhu.edu/people/ccarroll/papers/BufferStockTheory/#MPCLimits)
#
# This figure from the paper requires a very fine grid in order to capture the smooth variation in the MPC.  
#
# As a result, recomputation of the figure is too slow to be usable as a widget in real time (with current technology).

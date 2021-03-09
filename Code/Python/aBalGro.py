# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.10.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
#
#
# \begin{eqnarray}
# \Ex_{t}[\aLevBF_{t+1}/\aLevBF_{t}] & = & \Ex_{t}\left[\frac{\pLevBF_{t+1}\aNrm_{t+1}}{\pLevBF_{t}\aNrm_{t}}\right] \\ 
# & = & \Ex_{t}\left[\frac{\PermGroFac \permShk_{t+1} \pLevBF_{t}}{\pLevBF_{t}}\frac{\mNrm_{t+1}-\cNrm_{t+1}}{\aNrm_{t}}\right] \\
# & = & \left(\frac{\Ex_{t}[\PermGroFac \permShk_{t+1} \left(
# \Rfree/(\PermGroFac\permShk_{t+1})
# \aNrm_{t}+\tranShk_{t+1})-\cFunc(\Rfree/(\PermGroFac\permShk_{t+1})\aNrm_{t}+\tranShk_{t+1}
# \right)]}{\aNrm_{t}}\right) \\
# & = & \left(\frac{\PermGroFac \left(
# \Rfree
# \aNrm_{t}+1)-\Ex_{t}[\PermGroFac \permShk_{t+1}\cFunc(\Rfree/(\PermGroFac\permShk_{t+1})\aNrm_{t}+\tranShk_{t+1}
# \right)]}{\aNrm_{t}}\right) \\
# & \approx & \left(\frac{\PermGroFac (
# \Rfree
# \aNrm_{t}+1)-\Ex_{t}[\PermGroFac \permShk_{t+1}\left(\cFunc(\check{\aNrm})+\cFunc^{\prime}(\check{\aNrm})(\aNrm_{t+1}-\aNrm_{t})+\cFunc^{\prime\prime}(\check{\aNrm})(\aNrm_{t+1}-\aNrm_{t})^{2}/2\right)]}{\aNrm_{t}}\right) \\
# \end{eqnarray}
#

# %% [markdown]
#
#
# \begin{eqnarray}
# \PermGroFac & = & \left(\frac{\PermGroFac \left(
# \Rfree
# \aNrm_{t}+1)-\Ex_{t}[\PermGroFac \permShk_{t+1}\cFunc(\Rfree/(\PermGroFac\permShk_{t+1})\aNrm_{t}+\tranShk_{t+1}
# \right)]}{\aNrm_{t}}\right) \\
# \aNrm_{t} & = & \left(
# \Rfree
# \aNrm_{t}+1)-\Ex_{t}[ \permShk_{t+1}\cFunc(\Rfree/(\PermGroFac\permShk_{t+1})\aNrm_{t}+\tranShk_{t+1}
# \right)] \\
# \aNrm_{t} & = & \left(
# \Rfree
# \aNrm_{t}+1)-\Ex_{t}[ \permShk_{t+1}\cFunc(\Rfree/(\PermGroFac\permShk_{t+1})\aNrm_{t}+\tranShk_{t+1}
# \right)]
# \end{eqnarray}
#

# %%

# %% [markdown]
# Approximate around $\check{m}$
#
# \begin{eqnarray}
# \aNrm_{t}(1-\Rfree) & = & 
# 1 -\Ex_{t}[ \permShk_{t+1}\cFunc((\Rfree/\PermGroFac\permShk_{t+1})\aNrm_{t}+\tranShk_{t+1})]
# \\ \aNrm_{t}(1-\Rfree) & = & 
# 1 -\Ex_{t}[ \permShk_{t+1}\left(\cFunc(\hat{m})+(m_{t+1}-\check{m})+(1/2)\cFunc^{\prime\prime}(m_{t+1}-\hat{m})^{2}\right)]
# \\ &= &
# 1 - \hat{c}+(\check{m}-\check{m})\cFunc^{\prime}+\Ex_{t}[ \permShk_{t+1}\left((1/2)(m_{t+1}-\check{m})^{2}\cFunc^{\prime\prime}\right)] \\ 
# \check{m}-\cFunc(\check{m}) & = & 1 - \hat{c}+\Ex_{t}[ \permShk_{t+1}\left((1/2)(m_{t+1}-\check{m})^{2}\cFunc^{\prime\prime}\right)] \\ 
# \check{m} & = & 1 +\Ex_{t}[ \permShk_{t+1}\left((1/2)(m_{t+1}-\check{m})^{2}\cFunc^{\prime\prime}\right)]
# \\ \check{m} & = & 1 +\Ex_{t}[ \permShk_{t+1}\left((1/2)(m_{t+1}^{2}-2 m_{t+1}\check{m}+\check{m}^{2})\cFunc^{\prime\prime}\right)]
# \\ \check{m} & = & 1 +\Ex_{t}[ \permShk_{t+1}\left((1/2)(m_{t+1}^{2}-\check{m}^{2})\cFunc^{\prime\prime}\right)]
# \end{eqnarray}
#

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %% [markdown]
# \\
# & = & \left(\frac{\Ex_{t}[\PermGroFac \permShk_{t+1} \left(\Rfree/(\PermGroFac\permShk_{t+1})(\aNrm_{t}-\cNrm_{t})+\tranShk_{t+1}\right)-\cFunc(\PermGroFac \permShk_{t+1} \left(\Rfree/(\PermGroFac\permShk_{t+1})(\aNrm_{t}-\cNrm_{t})+\PermGroFac \permShk_{t+1}\tranShk_{t+1}\right)]}{\aNrm_{t}}\right) \\
# & = & \left(\frac{\Rfree (\aNrm_{t}-\cNrm_{t})+\PermGroFac}{\aNrm_{t}}\right)
# \end{eqnarray}
# but since $\Ex_{t}[\pLevBF_{t+1}]=\PermGroFac \pLevBF_{t}$ we have that
# \begin{eqnarray}
# \Ex_{t}[\mLevBF_{t+1}] & = & \Ex_{t}\left[\pLevBF_{t+1}\aNrm_{t+1}\right] \\ 
# & = & \pLevBF_{t} \Ex_{t}\left[\PermGroFac \permShk_{t+1} ((\Rfree/(\PermGroFac \permShk_{t+1} )(\aNrm_{t}-\cNrm_{t})+\tranShk_{t+1})\right] \\
# & = & \pLevBF_{t} \Ex_{t}\left[ \Rfree(\aNrm_{t}-\cNrm_{t})+\PermGroFac\right]
# \end{eqnarray}
#
# and so at the individual balanced growth point where $\Ex_{t}[\mLevBF_{t+1}] = \mLevBF_{t} =  \StE{\aNrm}$, we can write the last equation in the first block above as 
#
# \begin{align}
# \StE{\aNrm} & = \left(\frac{(\Rfree(\StE{\aNrm}-\cNrm)+\PermGroFac)\pLevBF_{t}}{\pLevBF_{t}\PermGroFac}\right)
# \\ & =  (\Rfree/\PermGroFac)(\StE{\aNrm}-\cNrm)+1)
# \\ (\StE{\aNrm} - 1)(\PermGroFac/\Rfree) & = (\StE{\aNrm}-\cNrm)
# \\ \cNrm & = \StE{\aNrm} - (\StE{\mNrm} - 1)(\PermGroFac/\Rfree) 
# \end{align}

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

# %%

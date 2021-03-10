# ---
# jupyter:
#   jupytext:
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
# \begin{eqnarray}
# \Ex_{t}[\mLevBF_{t+1}/\mLevBF_{t}] & = & \Ex_{t}\left[\frac{\pLevBF_{t+1}\mNrm_{t+1}(m_{t+1})}{\pLevBF_{t}\mNrm_{t}}\right] \\
# & = & \Ex_{t}\left[\frac{\PermGroFac \permShk_{t+1} \pLevBF_{t}}{\pLevBF_{t}}\frac{\mNrm_{t+1}}{\mNrm_{t}}\right] \\
# & = & \left(\frac{\Ex_{t}[\PermGroFac \permShk_{t+1} \left(\Rfree/(\PermGroFac\permShk_{t+1})(\mNrm_{t}-\cNrm_{t})+\PermGroFac \permShk_{t+1}\tranShk_{t+1}\right)]}{\mNrm_{t}}\right) \\
# & = & \left(\frac{\Rfree (\mNrm_{t}-\cNrm_{t})+\PermGroFac}{\mNrm_{t}}\right)
# \end{eqnarray}
# but since $\Ex_{t}[\pLevBF_{t+1}]=\PermGroFac \pLevBF_{t}$ we have that
# \begin{eqnarray}
# \Ex_{t}[\mLevBF_{t+1}] & = & \Ex_{t}\left[\pLevBF_{t+1}\mNrm_{t+1}\right] = \Ex_{t}\left[\PermGroFac\pLevBF_{t}\permShk_{t+1}\mNrm_{t+1}\right]  \\
# \Ex_{t}[\mLevBF_{t+1}/\mNrm_{t}\pLevBF_{t}]& = &\Ex_{t}\left[\PermGroFac \permShk_{t+1}\mNrm_{t+1}\right]/\mNrm_{t} \\
# \PermGroFac \mNrm_{t} & = & \Ex_{t}[\PermGroFac \permShk_{t+1} \left(\Rfree/(\PermGroFac\permShk_{t+1})(\mNrm_{t}-\cNrm_{t})+\PermGroFac \permShk_{t+1}\tranShk_{t+1}\right)] \\
# %\PermGroFac \mNrm_{t}  & = & \Ex_{t}[\Rfree(\mNrm_{t}-\cNrm_{t})]+\PermGroFac\\
# \mNrm_{t} & = & \mathcal{R}(\mNrm_{t}-\cNrm_{t})+1 \\
# \cNrm_{t}\mathcal{R} & = & \mNrm_{t}(\mathcal{R}-1)+1 \\
# \cNrm_{t} & = & 1+\mNrm_{t}(1-1/\mathcal{R})
# \end{eqnarray}
#
# and so at the individual balanced growth point where $\Ex_{t}[\mLevBF_{t+1}] = \mLevBF_{t} =  \StE{\mNrm}$, we can write the last equation in the first block above as
#
# \begin{align}
# \StE{\mNrm} & = \left(\frac{(\Rfree(\StE{\mNrm}-\cNrm)+\PermGroFac)\pLevBF_{t}}{\pLevBF_{t}\PermGroFac}\right)
# \\ & =  (\Rfree/\PermGroFac)(\StE{\mNrm}-\cNrm)+1)
# \\ (\StE{\mNrm} - 1)(\PermGroFac/\Rfree) & = (\StE{\mNrm}-\cNrm)
# \\ \cNrm & = \StE{\mNrm} - (\StE{\mNrm} - 1)(\PermGroFac/\Rfree)
# \end{align}
#

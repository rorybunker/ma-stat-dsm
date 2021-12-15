#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 29 13:23:50 2021

@author: rorybunker
"""

import matplotlib.pyplot as plt
plt.hist(ball_df.groupby(ball_df.index).count()['point'], bins = 100)

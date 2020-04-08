# -*- coding: utf-8 -*-
# **************************************************************************
# *
# * Authors:     David Herreros Calero (dherreros@cnb.csic.es)
# *
# * BCU, Centro Nacional de Biotecnologia, CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion@cnb.csic.es'
# *
# **************************************************************************

"""
@article{GRIGORE2010,
title = "Quantitative analysis of cryo-EM density map segmentation by watershed and scale-space filtering, and fitting of structures by alignment to regions",
journal = "Journal of Structural Biology",
volume = "170",
pages = "427 - 438",
year = "2010",
doi = "https://doi.org/10.1016/j.jsb.2010.03.007",
url = "https://www.sciencedirect.com/science/article/pii/S1047847710000845?via%3Dihub",
author = "Pintilie, Grigore D et al",
keywords = "Segment Map, Fit to Segments, Watershed Segmentation, Hierarchical Groupings",
abstract = "Cryo-electron microscopy produces 3D density maps of molecular machines, which consist of various molecular components such as proteins and RNA. Segmentation of individual components in such maps is a challenging task, and is mostly accomplished interactively. We present an approach based on the immersive watershed method and grouping of the resulting regions using progressively smoothed maps. The method requires only three parameters: the segmentation threshold, a smoothing step size, and the number of smoothing steps. We first apply the method to maps generated from molecular structures and use a quantitative metric to measure the segmentation accuracy. The method does not attain perfect accuracy, however it produces single or small groups of regions that roughly match individual proteins or subunits. We also present two methods for fitting of structures into density maps, based on aligning the structures with single regions or small groups of regions. The first method aligns centers and principal axes, whereas the second aligns centers and then rotates the structure to find the best fit. We describe both interactive and automated ways of using these two methods. Finally, we show segmentation and fitting results for several experimentally-obtained density maps."
}
"""

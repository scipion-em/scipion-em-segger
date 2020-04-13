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

import os, glob

import pyworkflow.viewer as pwviewer

import pwem.viewers.views as vi
from pwem.viewers.viewer_chimera import ChimeraView

from chimera import Plugin as chimera

from ..protocols.protocol_segment_map import ProtSegmentMap
from segger import Plugin

class SeggerViewer(pwviewer.Viewer):
    """ Wrapper to visualize different type of objects
    with the Xmipp program xmipp_showj
    """
    _environments = [pwviewer.DESKTOP_TKINTER]
    _targets = [ProtSegmentMap]

    def __init__(self, **kwargs):
        pwviewer.Viewer.__init__(self, **kwargs)
        self._views = []

    def _getObjView(self, obj, fn, viewParams={}):
        return vi.ObjectView(
            self._project, obj.strId(), fn, viewParams=viewParams)

    def _visualize(self, obj, **kwargs):
        views = []
        cls = type(obj)

        if issubclass(cls, ProtSegmentMap):
            filePath = self.chimeraViewFile()
            views.append(ChimeraView(filePath))

        return views

    def chimeraViewFile(self):
        outPath = self.protocol._getExtraPath()
        filePath = os.path.join(chimera.getHome(), 'share', 'Segger', 'viewChimera.py')
        f = open(filePath, "w")
        f.write('from chimera import runCommand\n')
        for segmentation in glob.glob(os.path.join(outPath, '*.seg')):
            f.write('runCommand("open %s")\n' % os.path.abspath(segmentation))
        f.close()
        return filePath

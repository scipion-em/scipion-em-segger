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

import os
import numpy as np

from pwem.objects import Volume
from pwem.protocols import EMProtocol
from pwem.emlib.image import ImageHandler

import pyworkflow.protocol.params as params
import pyworkflow.utils as pwutils

from pwem.viewers.viewer_chimera import Chimera

from segger import Plugin
from chimera import Plugin as chimera


class ProtSegmentMap(EMProtocol):
    """Protcol to perform the segmentation of maps into different regions based on
    the watershed algorithm
    For more information, follow the next link:
    https://cryoem.slac.stanford.edu/ncmi/resources/software/segger"""
    _label = 'segment map'

    def __init__(self, **kwargs):
        EMProtocol.__init__(self, **kwargs)

    # --------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        form.addSection(label='Input data')
        form.addParam('inputVolume', params.PointerParam, pointerClass='Volume', label='Input volume', important=True,
                      help='Select a Volume to be segmented')
        form.addSection(label='Mode')
        form.addParam('grouping', params.EnumParam, choices=['Smoothing', 'Connectivity'], default=0,
                      label='Grouping mode', display=params.EnumParam.DISPLAY_HLIST,
                      help='smoothing tends to work better at lower resolutions (4A and lower)\n'
                           'connectivity tends to work better at higher resolutions (4A and better)')
        form.addParam('smoothSteps', params.IntParam, default=4, condition='grouping == 0',
                      label='Number of smoothing steps')
        form.addParam('smoothStepSize', params.IntParam, default=3, condition='grouping == 0',
                      label='Smoothing step size')
        form.addParam('connectSteps', params.IntParam, default=10, condition='grouping == 1',
                      label='Number of connectivity steps')
        form.addSection('General parameters')
        form.addParam('minRegionSize', params.IntParam, default=1, label='Minimum region size',
                      help='Minimum region size in number of voxels (can be turned to A^3 by dividing by step size)\n'
                           'as below when set to 1, all regions will be kept; for a value of 5, only'
                           'regions that have at least 5 voxels would be kept after the first'
                           'segmentation step (1 means no regions are removed)')
        form.addParam('minContactVoxels', params.IntParam, default=0, label='Minimum contact voxels',
                      help='0 means no regions are removed')
        form.addParam('stopGroup', params.IntParam, default=1, label='Stop grouping',
                      help='When to stop the grouping process')
        form.addParam('mapThreshold', params.FloatParam, default=-1, label='Map threshold',
                      help='Only include voxels with map value above this values (by default, 3sigma above mean will be used')
        form.addSection(label='Output')
        form.addParam('pieces', params.EnumParam, label='Type of mask', choices=['Mask', 'Pieces', 'Both'], default=0,
                      display=params.EnumParam.DISPLAY_HLIST,
                      help='Mask: A single Volume containing several identifiers for each piece\n'
                           'Pieces: Several Volumes (files) one for each segmented region'
                           'Both: Mask + Pieces')

    # --------------------------- INSERT steps functions ----------------------
    def _insertAllSteps(self):
        self._insertFunctionStep('segmentationStep')
        self._insertFunctionStep('createOutputStep')

    # --------------------------- STEPS functions -----------------------------
    def segmentationStep(self):
        self.writeChimeraScript()
        args = '--nogui --silent --nostatus --script %s' % (os.path.join(chimera.getHome(), 'share', 'Segger', 'scriptChimera.py'))

        Chimera.runProgram(Plugin.getProgram(), args)

    def createOutputStep(self):
        file = 'segmask_' + pwutils.removeBaseExt(self.inputVolume.get().getFileName()) + '.mrc'
        file = self._getExtraPath(file)
        volume = Volume()
        volume.setLocation(file)
        volume.setSamplingRate(self.inputVolume.get().getSamplingRate())
        if self.pieces.get() == 0 or self.pieces.get() == 2:
            self._defineOutputs(outputSegmentation=volume)
            self._defineSourceRelation(self.inputVolume, volume)
        if self.pieces.get() == 1 or self.pieces.get() == 2:
            setVolumes = self._createSetOfVolumes()
            setVolumes.setSamplingRate(self.inputVolume.get().getSamplingRate())
            ih = ImageHandler()
            mask = ih.read(volume)
            mask = mask.getData()
            ids_mask = np.unique(mask)
            ids_mask = np.delete(ids_mask, 0)
            for idm in ids_mask:
                piece = Volume()
                piece.setLocation(self._getExtraPath('segmentation_group_%d.mrc' % int(idm)))
                piece.setSamplingRate(self.inputVolume.get().getSamplingRate())
                mask_logical = mask == idm
                pieceData = mask * mask_logical / idm
                img = ih.createImage()
                img.setData(pieceData)
                ih.write(img, piece)
                setVolumes.append(piece)
            self._defineOutputs(outputGroups=setVolumes)
            self._defineSourceRelation(self.inputVolume, setVolumes)



    # --------------------------- UTILS functions ----------------------------
    def writeChimeraScript(self):
        f = open(os.path.join(chimera.getHome(), 'share', 'Segger', 'scriptChimera.py'), "w")
        f.write("from chimerax.core.commands import run\n")
        f.write("run(session, 'open %s')\n" % self.inputVolume.get().getFileName())

        if self.grouping.get() == 0:
            groupMode = 'smoothing'
        else:
            groupMode = 'connectivity'

        contents = 'path = "%s"\n' \
                   'groupingMode = "%s"\n' \
                   'minRegionSize = %d\n' \
                   'minContactVoxels = %d\n' \
                   'stopAtNumberOfRegions = %d\n' \
                   'mapThreshold = %f\n' \
                   'if mapThreshold < 0:\n' \
                   '\tmapThreshold=None\n' \
                   'numSmoothingSteps = %d\n' \
                   'smoothingStepSize = %d\n' \
                   'numConnectivitySteps = %d\n' \
                   'outputRegions = []\n' \
                   'options = {}\n' \
                   'options["outputMapSize"] = "box"\n' \
                   'options["borderWidth"] = 4\n' \
                   'options["mask01"] = False\n' \
                   'from chimerax import segger as Segger\n' \
                   'from chimerax.core.models import Models\n' \
                   'from chimerax.map.volume import Volume\n' \
                   'from chimerax.segger import regions\n' \
                   'import numpy\n' \
                   'from chimerax.segger.segcmd import export_mask\n' \
                   'from chimerax.segger.segfile import write_segmentation\n' \
                   'maps = session.models.list(type=Volume)\n' \
                   'for dmap in maps:\n' \
                   '\tif mapThreshold == None :\n' \
                   '\t\tM = dmap.data.full_matrix()\n' \
                   '\t\tmapThreshold = numpy.average(M)+numpy.std(M)*3.0\n' \
                   '\tsmod = regions.Segmentation(dmap.name, session, dmap)\n' \
                   '\tsmod.calculate_watershed_regions ( dmap, mapThreshold )\n' \
                   '\tif minRegionSize > 1 :\n' \
                   '\t\tsmod.remove_small_regions(minRegionSize)\n' \
                   '\tif minContactVoxels > 0 :\n' \
                   '\t\tsmod.remove_contact_regions(minContactVoxels)\n' \
                   '\tif groupingMode == "smoothing" :\n' \
                   '\t\tsmod.smooth_and_group(numSmoothingSteps, smoothingStepSize, stopAtNumberOfRegions)\n' \
                   '\telif groupingMode == "connectivity" :\n' \
                   '\t\tsmod.group_connected_n (numConnectivitySteps, stopAtNumberOfRegions)\n' \
                   '\tregions_seg = smod.grouped_regions()\n' \
                   '\toutputN = len(regions_seg)\n' \
                   '\timport os\n' \
                   '\tmdir, mfile = os.path.split(dmap.data.path)\n' \
                   '\tmname, mext = os.path.splitext ( mfile )\n' \
                   '\tif outputN > 0 :\n' \
                   '\t\tfor i in range ( outputN ) :\n' \
                   '\t\t\treg = regions_seg[i]\n' \
                   '\tfileName = os.path.splitext(dmap.name)[0]\n' \
                   '\toutMask = os.path.join(path, "segmask_" + fileName + ".mrc") \n' \
                   '\toutSeg = os.path.join(path, "seg_" + fileName + ".seg") \n'\
                   '\texport_mask(smod, savePath=outMask)\n' \
                   '\twrite_segmentation(smod, path=outSeg)\n' % \
                   (self._getExtraPath(), groupMode, self.minRegionSize.get(), self.minContactVoxels.get(), self.stopGroup.get(),
                    self.mapThreshold.get(), self.smoothSteps.get(), self.smoothStepSize.get(), self.connectSteps.get())

        f.write(contents)
        f.close()

    # --------------------------- DEFINE info functions ----------------------
    def _methods(self):
        methodsMsgs = []
        if self.getOutputsSize() >= 1:
            if hasattr(self, 'outputSegmentation'):
                msg = ("Segmentation mask succesfully generated: %s\n" % self.outputSegmentation.getFileName())
                methodsMsgs.append(msg)
            if hasattr(self, 'outputGroups'):
                msg = ("Groups seprated into %d different masks\n" % len(self.outputGroups))
                methodsMsgs.append(msg)
        else:
            methodsMsgs.append("Segmentation not ready yet")
        return methodsMsgs

    def _summary(self):
        summary = []
        summary.append("Input Volume provided: %s\n"
                       % self.inputVolume.get().getFileName())
        if self.getOutputsSize() >= 1:
            if hasattr(self, 'outputSegmentation'):
                msg = ("Segmentation mask succesfully generated: %s\n" % self.outputSegmentation.getFileName())
                summary.append(msg)
            if hasattr(self, 'outputGroups'):
                msg = ("Groups seprated into %d different masks\n" % len(self.outputGroups))
                summary.append(msg)
        else:
            summary.append("Segmentations not ready yet.")
        return summary

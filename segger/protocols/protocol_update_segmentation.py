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

import os, configparser, glob
import numpy as np

from pwem.emlib.image import ImageHandler
from pwem.objects import Volume
from pwem.protocols import EMProtocol

import pyworkflow.protocol.params as params

import pyworkflow.utils as pwutils

from chimera.constants import CHIMERA_CONFIG_FILE
from pwem.viewers.viewer_chimera import (Chimera,
                                         sessionFile,
                                         chimeraMapTemplateFileName,
                                         chimeraPdbTemplateFileName)

from segger import Plugin
from ..convert import idMask2Segger


class ProtUpdateSeg(EMProtocol):
    """Protocol tu update an existing segmentation using Segger:
    https://cryoem.slac.stanford.edu/ncmi/resources/software/segger"""
    _label = 'update segmentation'

    def __init__(self, **kwargs):
        EMProtocol.__init__(self, **kwargs)

    # --------------------------- DEFINE param functions ----------------------
    def _defineParams(self, form):
        form.addSection(label='Input data')
        form.addParam('inputMask', params.PointerParam, pointerClass='Volume', label='Input mask', important=True,
                      help='Select a Mask of ids to be updated')
        form.addSection(label='Output')
        form.addParam('pieces', params.EnumParam, label='Type of mask', choices=['Mask', 'Pieces', 'Both'], default=0,
                      display=params.EnumParam.DISPLAY_HLIST,
                      help='Mask: A single Volume containing several identifiers for each piece\n'
                           'Pieces: Several Volumes (files) one for each segmented region'
                           'Both: Mask + Pieces')

    # --------------------------- INSERT steps functions ----------------------
    def _insertAllSteps(self):
        self._insertFunctionStep('updateStep', interactive=True)

    # --------------------------- STEPS functions -----------------------------
    def _convertInputStep(self):
        self.segPath = idMask2Segger(self._getExtraPath(), self.inputMask.get())

    def updateStep(self):
        if not os.path.isfile(self._getExtraPath(sessionFile)):
            self._convertInputStep()
            restoreSession = False
        else:
            restoreSession = True
        config = configparser.ConfigParser()
        _chimeraPdbTemplateFileName = \
            os.path.abspath(self._getExtraPath(
                chimeraPdbTemplateFileName))
        _chimeraMapTemplateFileName = \
            os.path.abspath(self._getExtraPath(
                chimeraMapTemplateFileName))
        _sessionFile = os.path.abspath(
            self._getExtraPath(sessionFile))
        protId = self.getObjId()
        config['chimerax'] = {'chimerapdbtemplatefilename':
                                  _chimeraPdbTemplateFileName % protId,
                              'chimeramaptemplatefilename':
                                  _chimeraMapTemplateFileName % protId,
                              'sessionfile': _sessionFile,
                              'enablebundle': True,
                              'protid': protId}
        with open(self._getExtraPath(CHIMERA_CONFIG_FILE),
                  'w') as configfile:
            config.write(configfile)

        self.writeChimeraScript()
        if not restoreSession:
            args = os.path.abspath(self._getExtraPath('scriptChimera.cxc'))
        else:
            args = os.path.abspath(self._getExtraPath(sessionFile))

        cwd = os.path.abspath(self._getExtraPath())
        Chimera.runProgram(Plugin.getProgram(), args, cwd=cwd)

        self._createOutputStep()

    def _createOutputStep(self):
        outMapPath = glob.glob(self._getExtraPath("*.mrc"))[0]
        volume = Volume()
        volume.setLocation(outMapPath)
        volume.setSamplingRate(self.inputMask.get().getSamplingRate())
        if self.pieces.get() == 0 or self.pieces.get() == 2:
            self._defineOutputs(outputSegmentation=volume)
            self._defineSourceRelation(self.inputMask, volume)
        if self.pieces.get() == 1 or self.pieces.get() == 2:
            baseOutFile = pwutils.removeBaseExt(outMapPath)
            setVolumes = self._createSetOfVolumes()
            setVolumes.setSamplingRate(self.inputMask.get().getSamplingRate())
            ih = ImageHandler()
            mask = ih.read(volume)
            mask = mask.getData()
            ids_mask = np.unique(mask)
            ids_mask = np.delete(ids_mask, 0)
            for idm in ids_mask:
                piece = Volume()
                piece.setLocation(self._getExtraPath(baseOutFile + '_group_%d.mrc' % int(idm)))
                piece.setSamplingRate(self.inputMask.get().getSamplingRate())
                mask_logical = mask == idm
                pieceData = mask * mask_logical / idm
                img = ih.createImage()
                img.setData(pieceData)
                ih.write(img, piece)
                setVolumes.append(piece)
            self._defineOutputs(outputGroups=setVolumes)
            self._defineSourceRelation(self.inputMask, setVolumes)

    # --------------------------- UTILS functions ----------------------------
    def writeChimeraScript(self):
        f = open(self._getExtraPath('scriptChimera.cxc'), "w")
        f.write("open %s\n" % os.path.abspath(self._getExtraPath('mask.seg')))
        f.write("vol all hide\n")
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
                       % self.inputMask.get().getFileName())
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

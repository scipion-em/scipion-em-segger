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

import os, threading

from pwem.viewers.viewer_chimera import Chimera

import pyworkflow.utils as pwutils
from pyworkflow.gui import TreeProvider, FileTreeProvider, ObjectBrowser

from ..convert import idMask2Segger


class SeggerTreeProvider(FileTreeProvider):
    """ Populate Tree from SetOfVolumes. """

    def __init__(self, volumeList, path):
        TreeProvider.__init__(self)
        self.volumeList = volumeList
        self._path = path

    def getColumns(self):
        return [('Volume', 150), ('Score', 50)]

    def getObjectInfo(self, volume):
        volumeName = os.path.basename(volume.getFileName())
        volumeName = os.path.splitext(volumeName)[0]
        return {'key': volumeName, 'parent': None,
                'text': volumeName, 'values': (round(volume.score.get(), 6))}

    def getObjectActions(self, obj):
        return []

    def getObjectPreview(self, obj):
        filename = obj.getFileName()
        fileHandler = self.getFileHandler(obj)
        return fileHandler._getImagePreview(filename), fileHandler._getImageString(filename)

    def _getObjectList(self):
        """Retrieve the object list"""
        return self.volumeList

    def getObjects(self):
        objList = self._getObjectList()
        return objList


class SeggerBrowser(ObjectBrowser):
    """
    This class extend from ListDialog to allow calling
    an Segger subprocess from a list of Volumes.
    """
    def __init__(self, window, provider, path):
        self.path = path
        ObjectBrowser.__init__(self, window.root, provider)
        self.tree.itemDoubleClick = self._itemDoubleClick

    def _itemDoubleClick(self, obj):
        self.volume = obj
        self.proc = threading.Thread(target=self.lanchSeggerForVolume, args=(self.volume,))
        self.proc.start()

    def lanchSeggerForVolume(self, volume):
        segFile = idMask2Segger(self.path, volume)
        filePath = self.chimeraViewFile(segFile)
        program = Chimera.getProgram()
        pwutils.runJob(None, program, filePath, env=Chimera.getEnviron())

    def chimeraViewFile(self, segFile):
        filePath = os.path.join(self.path, 'viewChimera.py')
        f = open(filePath, "w")
        f.write('from chimerax.core.commands import run\n')
        f.write('run(session, "open %s")\n' % os.path.abspath(segFile))
        f.write('run(session, "vol all hide")\n')
        f.close()
        return filePath

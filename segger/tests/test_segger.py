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

from pwem.protocols import ProtImportVolumes

from pyworkflow.tests import BaseTest, setupTestProject
from pyworkflow.tests.tests import DataSet

from ..protocols.protocol_segment_map import ProtSegmentMap

class TestSeggerBase(BaseTest):
    @classmethod
    def setUpClass(cls):
        setupTestProject(cls)

    @classmethod
    def setData(cls, projectData='relion_tutorial'):
        cls.dataset = DataSet.getDataSet(projectData)
        cls.volume = cls.dataset.getFile('volumes/reference.mrc')

class TestSegmentMap(TestSeggerBase):
    '''This class checks if the protocol to segment_map
    works properly'''

    @classmethod
    def setUpClass(cls):
        setupTestProject(cls)
        TestSeggerBase.setData()

    def _runSegmentation(self, mode='', output=''):

        if mode == 'Connectivity':
            grouping = 1
        elif mode == 'Smoothing':
            grouping = 0

        if output == 'Mask':
            pieces = 0
        elif output == 'Pieces':
            pieces = 1
        elif output == 'Both':
            pieces = 2

        protImportVolumes = self.newProtocol(ProtImportVolumes,
                                             filesPath=self.volume,
                                             samplingRate=1.0)

        self.launchProtocol(protImportVolumes)

        self.assertIsNotNone(protImportVolumes.outputVolume,
                             "There was a problem with volume output")

        protSegmentationMap = self.newProtocol(ProtSegmentMap,
                                               objLabel='Segmentation - %s - Output %s' % (mode, output),
                                               inputVolume=protImportVolumes.outputVolume,
                                               grouping=grouping,
                                               pieces = pieces)

        self.launchProtocol(protSegmentationMap)
        return protSegmentationMap

    def test_SegmemntMap_SmoothingMask(self):
        protSegmentationMap = self._runSegmentation(mode='Connectivity', output='Mask')

        outputMask = getattr( protSegmentationMap, 'outputSegmentation', None)
        self.assertTrue(outputMask)

        return protSegmentationMap

    def test_SegmemntMap_SmoothingGroups(self):
        protSegmentationMap = self._runSegmentation(mode='Connectivity', output='Pieces')

        outputGroups = getattr( protSegmentationMap, 'outputGroups', None)
        self.assertTrue(outputGroups)

        return protSegmentationMap

    def test_SegmemntMap_SmoothingBoth(self):
        protSegmentationMap = self._runSegmentation(mode='Connectivity', output='Both')

        outputMask = getattr( protSegmentationMap, 'outputSegmentation', None)
        self.assertTrue(outputMask)

        outputGroups = getattr( protSegmentationMap, 'outputGroups', None)
        self.assertTrue(outputGroups)

        return protSegmentationMap

    def test_SegmemntMap_ConnectMask(self):
        protSegmentationMap = self._runSegmentation(mode='Smoothing', output='Mask')

        outputMask = getattr( protSegmentationMap, 'outputSegmentation', None)
        self.assertTrue(outputMask)

        return protSegmentationMap
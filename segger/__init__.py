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

import pwem

from chimera import Plugin as chimera_plugin


_logo = "icon.png"
_references = ['GRIGORE2010']

class Plugin(pwem.Plugin):
    _supportedVersions = 'V2_3'

    @classmethod
    def _defineVariables(cls):
        pass

    @classmethod
    def getEnviron(cls):
         return chimera_plugin.getEnviron()

    @classmethod
    def runChimeraProgram(cls, program, args="", cwd=None):
        """ Internal shortcut function to launch chimera program. """
        chimera_plugin.runChimeraProgram(program, args="", cwd=cwd)

    @classmethod
    def getProgram(cls, progName="chimera"):
        """ Return the program binary that will be used. """
        chimera_plugin.getProgram(progName)

    @classmethod
    def defineBinaries(cls, env):
        SW_CH = env.getEmFolder()
        command = '%s install.py %s/chimera-1.13.1/' % (env.getPython(), SW_CH)
        segger_commands = [(command, '../chimera-1.13.1/share/Segger')]

        env.addPackage('segger',
                       version='2.3',
                       tar='segger-2.3.tar.gz',
                       commands=segger_commands,
                       default=True)

#
# Copyright (C) 2009 Michael Budde
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
# 

import os, os.path, subprocess, shutil

import Task, Build, Utils
from Constants import *


class FOXTask(Task.TaskBase):

    dll_path = 'src/.libs'

    def get_dll_name(self):
        return 'libFOX-%s-0.dll' % getattr(self, 'foxver', '1.6')
    dll_name = property(get_dll_name)

    def foxpath(self, *paths):
        foxdir = getattr(self, 'foxdir', 'fox')
        return os.path.join(self.bld.curdir, foxdir, *paths)

    def runnable_status(self):
        if not os.path.isfile(self.dll_name):
            return RUN_ME
        return SKIP_ME

    def __str__(self):
        return 'FOX task: building FOX library\n'

    def run(self):
        old_dir = os.getcwd()
        os.chdir(self.foxpath())

        if not os.path.isfile(self.foxpath(self.dll_path, self.dll_name)):
            # TODO: write to log file
            build_cmds = (
                ['autoconf'],
                ['./configure', '--host=i586-mingw32msvc',
                 '--with-mingw32=/usr/i586-mingw32msvc', '--enable-shared',
                 '--enable-static'],
                ['make']
            )
            for cmd in build_cmds:
                subprocess.call(cmd)

        if os.path.isfile(self.foxpath(self.dll_path, self.dll_name)):
            shutil.copy(self.foxpath(self.dll_path, self.dll_name),
                        os.path.join(self.bld.bldnode.abspath(), 'default'))

        os.chdir(old_dir)


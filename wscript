#! /usr/bin/env python
# encoding: utf-8
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

VERSION='0.0.1'
APPNAME='ekg-renamer'

srcdir = '.'
blddir = '_build_'

foxdir = 'fox'
foxver = '1.6'

import os, os.path, subprocess

import Scripting, Options, Utils
import buildfox

def set_options(opt):
    #opt.tool_options('qt4')
    opt.tool_options('compiler_cxx')
    opt.tool_options('gnu_dirs')
    opt.add_option('--run', '-r', action='store_true', default=False,
                   help='Execute the program after it is compiled')
    opt.add_option('--reset', action='store_true',
                   help='Reset FOX directory')

def configure(conf):
    mingw_progs = [
        ('AR', 'ar'),
        ('RANLIB', 'ranlib'),
        ('CC', 'gcc'),
        ('CPP', 'g++'),
        ('CXX', 'g++'),
        ('LINK_CC', 'gcc'),
        ('LINK_CXX', 'g++'),
        ('WINRC', 'windres')
    ]
    for var, prog in mingw_progs:
        conf.env[var] = 'i586-mingw32msvc-' + prog
    conf.env['CXXFLAGS'] = '-g'

    conf.check_tool('compiler_cxx')
    conf.check_tool('gnu_dirs')

    conf.env['LIBPATH_FOX'] = os.path.abspath(blddir)
    conf.env['LINKFLAGS_FOX'] = '-lFOX-1.6-0'

    #mingw_env = conf.env.copy()
    #mingw_env.set_variant('mingw')
    #conf.set_env_name('mingw', mingw_env)

    #conf.setenv('mingw')

def build(bld):
    fox = buildfox.FOXTask()
    bld.add_group()

    obj = bld.new_task_gen(
        features = 'cxx cprogram',
        target   = 'ekg-renamer',
        includes = 'src %s/include' % foxdir,
        uselib   = 'FOX')
    obj.find_sources_in_dirs('src')

    def post(bld):
        cmd = ['wine', '%s/default/ekg-renamer.exe' % blddir]
        if Options.options.run:
            Utils.pprint('YELLOW', 'Running ekg-renamer.exe')
            subprocess.call(cmd)

    bld.add_post_fun(post)

def distclean(bld):
    Scripting.distclean(bld)
    cmd = ('git clean -fdx %s' % foxdir).split()
    subprocess.call(cmd)
    if Options.options.reset:
        cmd = ('git co HEAD %s' % foxdir).split()
        subprocess.call(cmd)

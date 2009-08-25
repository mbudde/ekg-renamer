# -*- coding: latin1 -*-
#
# Copyright (C) 2009  Michael Budde
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the University nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE REGENTS AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
# 

__author__    = 'Michael Budde <mbudde@gmail.com>'
__copyright__ = 'Copyright (C) 2009  Michael Budde'
__license__   = 'BSD License'

import sys
import os
import os.path
import subprocess
import glob
import shutil
import cPickle


ADOBE_READER_PATH = 'C:\Program Files\Adobe\Reader*\Reader\AcroRd32.exe'
PDFTK_PATH        = 'C:\Program Files\GUIPDFTK\pdftk.exe'


def catch_eof_error(fun):
   def _():
       try:
           fun()
       except EOFError, KeyboardInterrupt:
           print
   return _

def input(prompt=''):
    prompt += prompt and '\n> ' or '> '
    return raw_input(prompt)

def input_with_default(prompt='', default=None):
    if default:
        prompt += ' [%s]' % default
    ans = input(prompt)
    if not ans and default:
        return default
    else:
        return ans

def input_with_choice(prompt='', good=('y', 'j'), bad=('n',)):
    prompt += ' [%s%s]' % (''.join(good), ''.join(bad))
    while True:
        ans = input(prompt)
        if ans.lower() in good:
            return True
        elif ans.lower() in bad:
            return False


class PDFSplitter(object):

    def __init__(self):
        self.cmd = None
        self.path = self._get_path()

    def split(self, pdf):
        if self.cmd:
            self.wait()
        self.cmd = subprocess.Popen(self._create_cmd(pdf))

    def wait(self):
        if self.cmd:
            print 'Venter på PDF filen bliver splittet...'
            self.cmd.wait()
            self.cmd = None

    def _create_cmd(self, pdf):
        raise NotImplemented()

    def _get_path(self):
        raise NotImplemented()


class PDFTKSplitter(PDFSplitter):

    def _get_path(self):
        path = os.getenv('PDFTK')
        if path:
            return os.path.abspath(path)
        if os.name == 'nt':
            if os.path.isfile('pdftk.exe'):
                return os.path.abspath('pdftk.exe')
            if os.path.isfile(PDFTK_PATH):
                os.path.abspath(PDFTK_PATH)
        elif os.name == 'posix':
            for path in os.getenv('PATH', '').split(os.pathsep):
                path = os.path.join(path, 'pdftk')
                if os.path.isfile(path):
                    return path
        print 'Kunne ikke finde pdftk. Sæt PDFTK variablen.'
        sys.exit(1)

    def _create_cmd(self, pdf):
        return [self.path, pdf, 'burst']


def get_pdf_reader():
    path = os.getenv('PDF_READER')
    if path:
        return path
    paths = glob.glob(ADOBE_READER_PATH)
    if paths and os.path.isfile(paths[-1]):
       return paths[-1]
    print 'Kunne ikke finde en PDF læser. Sæt PDF_READER variablen.'
    sys.exit(1)


@catch_eof_error
def main():
    splitter = PDFTKSplitter()

    ans = input_with_choice('Split PDF fil?')
    if ans:
        pdf = input('Hvilken PDF?')
        if os.path.exists(pdf):
            pdf = os.path.abspath(pdf)
            splitdir = os.path.splitext(pdf)[0]
            if os.path.exists(splitdir) and not os.path.isdir(splitdir):
                i = 0
                while True:
                    new_dir = '%s_%02d' % (splitdir, i)
                    if not os.path.exists(new_dir) or os.path.isdir(new_dir):
                        splitdir = new_dir
                        break
                    else:
                        i += 1
                        if i > 99:
                            sys.exit(1)
            if not os.path.exists(splitdir):
                os.mkdir(splitdir)
            os.chdir(splitdir)
            splitter.split(pdf)
        else:
            print 'PDF filen findes ikke'
            sys.exit(1)
    else:
        mappe = input('Hvilken mappe?')
        if os.path.exists(mappe):
            os.chdir(mappe)
        else:
            print 'Mappe findes ikke'
            sys.exit(1)

    procpr = {}
    if os.path.isfile('cpr-data.txt'):
        with open('cpr-data.txt', 'r') as cprfile:
            procpr = cPickle.load(cprfile)
            for pro, cpr in procpr.items():
                print '%s: %s' % (pro, cpr)

    print 'Angiv liste med sammenhængende PRO og CPR numre.'
    print 'PRO og CPR nummer skal være adskilt af et mellemrum, komma (fx. `12345,112233-5566\').'
    print 'Afslut med en blank linje.'
    while True:
        line = input()
        if line == '': break
        if ',' in line:
            line = line.split(',')
        else:
            line = line.split()
        procpr[line[0]] = line[1]

    with open('cpr-data.txt', 'w') as cprfile:
        cPickle.dump(procpr, cprfile)

    splitter.wait()

    files = glob.glob('pg_*.pdf')
    for f in files:
        pdf_reader = get_pdf_reader()
        subprocess.call([pdf_reader, os.path.join(os.getcwd(), f)])
        pronr = input('PRO nr.:')
        if pronr not in procpr:
            print 'Kunne ikke finde et CPR nr. sammenhørende med PRO nr. %s' % pronr
            nyt_pronr = input_with_default('PRO nr.:', pronr)
            if nyt_pronr != '':
                pronr = nyt_pronr
                if pronr not in procpr:
                    cprnr = input('CPR nr.:')
                    if cprnr != '':
                        procpr[pronr] = cprnr
                    else:
                        print 'Fil %s ignoreret' % f
                        continue
            else:
                print 'Fil %s ignoreret' % f
                continue

        dest = procpr[pronr] + '.pdf'
        if os.path.exists(dest):
            print 'PRO nummeret er allerede brugt, ignorer filen.'
            continue
        print 'Flytter %s til %s' % (f, dest)
        shutil.move(f, dest)

    raw_input('Færdig. Tryk ENTER for at afslutte.')

if __name__ == '__main__':
    main()

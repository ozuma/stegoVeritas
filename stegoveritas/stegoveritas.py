#!/usr/bin/env python3

from . import Colorer

import logging
logging.basicConfig(level=logging.WARN)

logger = logging.getLogger('StegoVeritas')

import binascii
import os, os.path
import argparse
from .config import *
from .version import version

import magic
import time
import shutil

from .install_deps import required_packages

class StegoVeritas(object):

    def __init__(self, args=None):
        """
        Args:
            args (list, optional): Arguments as if you passed them via the command line (i.e.: ['-out','directory','-meta'])
        """
        
        self._preflight()
        self._parse_args(args)
        self.modules = []


    def run(self):
        """Run analysis on the file."""
        for module in modules.iter_modules(self):
            print('Running Module: ' + module.__class__.__name__)
            print(module.description)
            module.run()
            self.modules.append(module)

    def test_output(self, thing):
            """
            Args:
                thing (bytes): Renerally from the dump functions
                    ex: thing = b'\x01\x02\x03'

            Returns:
                Nothing. Move output into keep directory if it's worth-while    

            
            Test if output is worth keeping. If it is, move it into the results directory.
            Initially, this is using the Unix file command on the output and checking for non "Data" returns
            """
            
            assert type(thing) == bytes, 'test_output got unexpected thing type of {}'.format(type(thing))

            # TODO: Test new logic...
            # TODO: Iterate through binary offset to find buried data

            m = magic.from_buffer(thing,mime=True)

            # Generic Output
            if m != 'application/octet-stream':
                m = magic.from_buffer(thing,mime=False)
                print("Found something worth keeping!\n{0}".format(m))
                # Save it to disk
                # TODO: Minor race condition here if we end up multi-processing
                with open(os.path.join(self.results_directory, str(time.time())), "wb") as f:
                    f.write(thing)
            
            # TODO: Check if strings of output contain a known word, save if so.

    def _preflight(self):
        """Checks for missing requirements."""
        
        missing_packages = []

        for package in required_packages:
            if shutil.which(package) is None:
                missing_packages.append(package)

        if missing_packages != []:
            logger.error('Missing the following required packages: ' + ', '.join(missing_packages))
            logger.error('Either install them manually or run \'stegoveritas_install_deps\'.')

    def _parse_args(self, args=None):

        parser = argparse.ArgumentParser(description='Yet another Stego tool',
                epilog = 'Have a good example? Wish it did something more? Submit a ticket: https://github.com/bannsec/stegoVeritas')
        parser.add_argument('-out',metavar='dir',type=str, help='Directory to place output in. Defaults to ./results',default=os.path.abspath('./results'))
        parser.add_argument('-meta',action='store_true',help='Check file for metadata information')
        parser.add_argument('-imageTransform',action='store_true',help='Perform various image transformations on the input image and save them to the output directory')
        parser.add_argument('-bruteLSB',action='store_true',help='Attempt to brute force any LSB related stegonography.')
        parser.add_argument('-colorMap',nargs="*",metavar='N',type=int, default=None, help='Analyze a color map. Optional arguments are colormap indexes to save while searching')
        parser.add_argument('-colorMapRange',nargs=2,metavar=('Start','End'),type=int,help='Analyze a color map. Same as colorMap but implies a range of colorMap values to keep')
        parser.add_argument('-extractLSB',action='store_true',help='Extract a specific LSB RGB from the image. Use with -red, -green, -blue, and -alpha')
        parser.add_argument('-red',nargs='+',metavar='index',type=int)
        parser.add_argument('-green',nargs='+',metavar='index',type=int)
        parser.add_argument('-blue',nargs='+',metavar='index',type=int)
        parser.add_argument('-alpha',nargs='+',metavar='index',type=int)
        parser.add_argument('-trailing',action='store_true',help='Check for trailing data on the given file')
        parser.add_argument('-debug', action='store_true', help='Enable debugging logging.')
        parser.add_argument('file_name',metavar='file',type=str, default=False, help='The file to analyze')

        self.args = parser.parse_args(args)

        if self.args.debug:
            logging.root.setLevel(logging.DEBUG)

        self.file_name = self.args.file_name
        self.results_directory = self.args.out
    
    ##############
    # Properties #
    ##############

    @property
    def file_name(self) -> str:
        return self.__file_name

    @file_name.setter
    def file_name(self, file_name: str) -> None:
        
        full_path = os.path.abspath(file_name)
        
        if not os.path.exists(full_path):
            logger.error('Cannot find file "{}"'.format(full_path))
            exit(1)

        logger.info('Analyzing file: ' + full_path)
        self.__file_name = full_path

    @property
    def results_directory(self) -> str:
        return self.__results_directory

    @results_directory.setter
    def results_directory(self, results_directory: str) -> None:
        full_path = os.path.abspath(results_directory)

        if os.path.exists(full_path) and not os.path.isdir(full_path):
            logger.error('Output path exists and is not a directory.')
            exit(1)

        os.makedirs(full_path, exist_ok=True)
        
        logger.info('Results Directory: ' + full_path)
        self.__results_directory = results_directory

    @property
    def modules(self) -> list:
        """list: List of all modules that have been run. NOTE: This will only be populated AFTER 'run' has been called and the modules themselves have been run."""
        return self.__modules

    @modules.setter
    def modules(self, modules):
        self.__modules = modules


def main(args=None):
    veritas = StegoVeritas(args=args)
    veritas.run()

from . import modules

if __name__ == '__main__':
    main()

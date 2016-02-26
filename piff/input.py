# Copyright (c) 2016 by Mike Jarvis and the other collaborators on GitHub at
# https://github.com/rmjarvis/Piff  All rights reserved.
#
# Piff is free software: Redistribution and use in source and binary forms
# with or without modification, are permitted provided that the following
# conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the disclaimer given in the accompanying LICENSE
#    file.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

"""
.. module:: input
"""

from __future__ import print_function
import glob

def process_input(config, logger):
    """Parse the input field of the config dict.

    :param config:      The configuration dict.
    :param logger:      A logger object for logging debug info.

    :returns: images, stars, kwargs
    """
    import piff

    if 'input' not in config:
        raise ValueError("config dict has no input field")
    config_input = config['input']

    # Get the class to use for handling the input data
    # Default type is 'Files'
    # Not sure if this is what we'll always want, but it would be simple if we can make it work.
    input_handler_class = eval('piff.Input' + config_input.pop('type','Files'))

    # Read any other kwargs in the input field
    kwargs = input_handler_class.parseKwargs(config_input)

    # Build handler object
    input_handler = input_handler_class(**kwargs)

    images = input_handler.readImages()
    stars = input_handler.readStarCatalogs()

    return images, stars

class InputHandler(object):
    """The base class for handling inputs for building a Piff model.

    This is essentially an abstract base class intended to define the methods that should be
    implemented by any derived class.
    """
    @classmethod
    def parseKwargs(cls, config_input):
        """Parse the input field of a configuration dict and return the kwargs to use for
        initializing an instance of the class.

        The base class implementation just returns the kwargs as they are, but derived classes
        might want to override this if they need to do something more sophisticated with them.

        :param config_input:    The input field of the configuration dict, config['input']

        :returns: a kwargs dict to pass to the initializer
        """
        return config_input

    def readImages(self):
        """Read in the images from whatever the input source is and return them.

        :returns: a list of galsim.Image instances
        """
        raise NotImplemented("Derived classes must define the readImages function")

    def readStarCatalogs(self):
        """Read in the star catalogs and return lists of positions for each star in each image.

        :returns: a list of lists of galsim.PositionD instances
        """
        raise NotImplemented("Derived classes must define the readStarCatalogs function")


class InputFiles(InputHandler):
    """An InputHandler than just takes a list of image files and catalog files.

    :param images:      Either a string (e.g. "some_dir/*.fits.fz") or a list of strings
                        (e.g. ["file1.fits", "file2.fits"]) listing the image files to read.
    :param cats:        Either a string (e.g. "some_dir/*.fits.fz") or a list of strings
                        (e.g. ["file1.fits", "file2.fits"]) listing the catalog files to read.
    :param xcol:        The name of the X column in the input catalogs. [default: 'x']
    :param ycol:        The name of the Y column in the input catalogs. [default: 'y']
    :param image_hdu:   The hdu to use in the image files. [default: None, which means use either
                        0 or 1 as typical given the compression sceme of the file]
    :param cat_hdu:     The hdu to use in the catalgo files. [default: 1]
    """
    def __init__(self, images, cats, xcol='x', ycol='y', image_hdu=None, cat_hdu=1):
        if isinstance(images, basestring):
            self.image_files = glob.glob(images)
        else:
            self.image_files = images
        if isinstance(cats, basestring):
            self.cat_files = glob.glob(cats)
        else:
            self.cat_files = cats
        self.xcol = xcol
        self.ycol = ycol
        self.image_hdu = image_hdu
        self.cat_hdu = cat_hdu

    def readImages(self):
        """Read in the images from the input files and return them.

        :returns: a list of galsim.Image instances
        """
        import galsim
        images = [ galsim.fits.read(fname, hdu=self.image_hdu) for fname in self.image_files ]
        return images

    def readStarCatalogs(self):
        """Read in the star catalogs and return lists of positions for each star in each image.

        :returns: a list of lists of galsim.PositionD instances
        """
        import fitsio
        import galsim
        cats = []
        for fname in self.cat_files:
            fits = fitsio.FITS(fname)
            xlist = fits[self.cat_hdu].read_column(self.xcol)
            ylist = fits[self.cat_hdu].read_column(self.ycol)
            cats.append([ galsim.PositionD(float(x),float(y)) for x,y in zip(xlist,ylist) ])
        return cats


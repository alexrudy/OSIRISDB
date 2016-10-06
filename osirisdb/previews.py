# -*- coding: utf-8 -*-
"""
Generate previews
"""

import collections
import attr
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

@attr.s
class _Preview(collections.Mapping):
    """A collection of preview functions."""
    _data = attr.ib(default=attr.Factory(dict), init=False)
    
    def register(self, kind):
        """File kind-specific preview"""
        
        def _decorator(f):
            self._data[kind] = f
            return f
        return _decorator
    
    def __getitem__(self, key):
        """Get the appropriate preview function."""
        return self._data[key]
    
    def __len__(self):
        return self._data.__len__()
    
    def __iter__(self):
        return self._data.__iter__()
    
Preview = _Preview()

@Preview.register('fits')
def preview_fits(datafile):
    """Generate a preview for a FITS file"""
    with datafile.open() as HDUs:
        primary_hdu = HDUs[0]
        dispatch_methods = {
            1:preview_spectrum, 
            2:preview_image,
            3:preview_cube,
        }
        figure = dispatch_methods[primary_hdu.data.ndim](primary_hdu)
    return figure


def wavelength(HDU):
    """Get wavelength from an HDU with WCS."""
    import astropy.units as u
    from astropy.wcs import WCS
    import numpy as np
    
    shape = HDU.data.shape
    wcs = WCS(HDU.header)
    
    wave_axis = HDU.data.ndim - wcs.axis_type_names.index('WAVE') - 1
    pix = np.zeros((shape[wave_axis], len(wcs.axis_type_names)))
    
    pix[:,0] = np.arange(shape[wave_axis])
    world = wcs.all_pix2world(pix, 1)
    wl = world[:,0] * u.Unit(u.m)
    return wl.to(u.Unit(HDU.header.get("CUNIT{0}".format(wcs.axis_type_names.index('WAVE')),u.m)))

def preview_spectrum(HDU):
    """Preview a 1D spectrum"""
    from astropy.visualization import quantity_support
    with quantity_support():
        fig, ax = plt.subplots(1,1)
        wave = wavelength(HDU)
        ax.plot(wave, HDU.data)
        ax.set_xlabel("Wavelength ({0:latex})".format(wave.unit))
        ax.set_ylabel("Flux")
    return fig

def preview_image(HDU):
    """For an image, preview"""
    from astropy.visualization import quantity_support, PercentileInterval, LogStretch
    from astropy.visualization.mpl_normalize import ImageNormalize
    from astropy.wcs import WCS
    
    with quantity_support():
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1, projection=WCS(HDU.header))
        image = PercentileInterval(90)(HDU.data)
        norm = ImageNormalize(stretch=LogStretch())
        im = ax.imshow(image, norm=norm, cmap='Blues_r')
        fig.colorbar(im, ax=ax)
    return fig
    
def preview_cube(HDU):
    """Preview a datacube"""
    from astropy.visualization import quantity_support, PercentileInterval, LogStretch
    from astropy.visualization.mpl_normalize import ImageNormalize
    from astropy.wcs import WCS
    import numpy as np
    
    wcs = WCS(HDU.header)
    wave_axis = HDU.data.ndim - wcs.axis_type_names.index('WAVE') - 1
    wcs = wcs.dropaxis(wcs.axis_type_names.index('WAVE'))
    image = np.median(HDU.data, axis=wave_axis)
    
    with quantity_support():
        fig = plt.figure()
        ax = fig.add_subplot(1,1,1, projection=wcs)
        image = PercentileInterval(90)(image)
        norm = ImageNormalize(stretch=LogStretch())
        im = ax.imshow(image, norm=norm, cmap='Blues_r')
        fig.colorbar(im, ax=ax)
    return fig
    
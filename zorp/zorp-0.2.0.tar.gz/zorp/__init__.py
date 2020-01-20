from distutils.version import LooseVersion

__version__ = '0.2.0'
__version_info__ = tuple(LooseVersion(__version__).version)

__all__ = [
    'parsers',
    'readers',
    'sniffers',
]

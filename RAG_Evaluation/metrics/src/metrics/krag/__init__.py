# krag/__init__.py

try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    # For older Python versions
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("krag")
except PackageNotFoundError:
    __version__ = "unknown"


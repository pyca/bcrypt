import os
import platform
import re
import shutil
import subprocess
import sys

from setuptools import setup

try:
    from setuptools_rust import RustExtension
except ImportError:
    print(
        """
        =============================DEBUG ASSISTANCE==========================
        If you are seeing an error here please try the following to
        successfully install bcrypt:

        Upgrade to the latest pip and try again. This will fix errors for most
        users. See: https://pip.pypa.io/en/stable/installing/#upgrading-pip
        =============================DEBUG ASSISTANCE==========================
        """
    )
    raise

if platform.python_implementation() == "PyPy":
    if sys.pypy_version_info < (2, 6):
        raise RuntimeError(
            "bcrypt is not compatible with PyPy < 2.6. Please upgrade PyPy to "
            "use this library."
        )


try:
    setup(
        rust_extensions=[
            RustExtension(
                "bcrypt._bcrypt",
                "src/_bcrypt/Cargo.toml",
                py_limited_api=True,
                rust_version=(
                    ">=1.64.0"
                    if os.environ.get("BCRYPT_ALLOW_RUST_163", "0") != "0"
                    else ">=1.63.0"
                ),
            ),
        ],
    )
except:
    # Note: This is a bare exception that re-raises so that we don't interfere
    # with anything the installation machinery might want to do. Because we
    # print this for any exception this msg can appear (e.g. in verbose logs)
    # even if there's no failure. For example, SetupRequirementsError is raised
    # during PEP517 building and prints this text. setuptools raises SystemExit
    # when compilation fails right now, but it's possible this isn't stable
    # or a public API commitment so we'll remain ultra conservative.

    import pkg_resources

    print(
        """
    =============================DEBUG ASSISTANCE=============================
    If you are seeing a compilation error please try the following steps to
    successfully install bcrypt:
    1) Upgrade to the latest pip and try again. This will fix errors for most
       users. See: https://pip.pypa.io/en/stable/installing/#upgrading-pip
    2) Ensure you have a recent Rust toolchain installed. bcrypt requires
       rustc >= 1.64.0. (1.63 may be used by setting the BCRYPT_ALLOW_RUST_163
       environment variable)
    """
    )
    print(f"    Python: {'.'.join(str(v) for v in sys.version_info[:3])}")
    print(f"    platform: {platform.platform()}")
    for dist in ["pip", "setuptools", "setuptools_rust"]:
        try:
            version = pkg_resources.get_distribution(dist).version
        except pkg_resources.DistributionNotFound:
            version = "n/a"
        print(f"    {dist}: {version}")
    version = "n/a"
    if shutil.which("rustc") is not None:
        try:
            # If for any reason `rustc --version` fails, silently ignore it
            rustc_output = subprocess.run(
                ["rustc", "--version"],
                capture_output=True,
                timeout=0.5,
                encoding="utf8",
                check=True,
            ).stdout
            version = re.sub("^rustc ", "", rustc_output.strip())
        except subprocess.SubprocessError:
            pass
    print(f"    rustc: {version}")

    print(
        """\
    =============================DEBUG ASSISTANCE=============================
    """
    )
    raise

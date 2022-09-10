from pathlib import Path

from setuptools import find_packages, setup

this_directory = Path(__file__).parent
long_description = (this_directory / "readme.md").read_text()

exec(open("splatplost/version.py").read())

# noinspection PyUnresolvedReferences
version = __version__

setup(
        name='splatplost',
        version=version,
        scripts=['splatplost/splatplot', 'splatplost/splatplan', 'splatplost/gui/splatplost'],
        package_dir={'splatplost': 'splatplost'},
        packages=find_packages(),
        url='https://github.com/Victrid/splatplost',
        license='GPLv3',
        author='Weihao Jiang',
        author_email='weihau.chiang@gmail.com',
        description='A software-based SplatPost plotter.',
        long_description=long_description,
        long_description_content_type='text/markdown',
        classifiers=[
            "Development Status :: 3 - Alpha",
            ],
        install_requires=[
            "numpy~=1.23.2",
            "Pillow~=9.2.0",
            "setuptools~=65.3.0",
            "scipy~=1.9.1",
            "tqdm~=4.64.0",
            "scikit-image~=0.19.3",
            "libnxctrl~=0.1.7",
            "tsp-solver2~=0.4.1",
            "PyQt6~=6.3.1"
            ],
        package_data={
            "splatplost": ["splatplost/gui/*.ui"]
            }
        )

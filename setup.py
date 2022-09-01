from setuptools import setup, find_packages

setup(
        name='splatplost',
        version='0.1.1',
        scripts=['splatplost/splatplot', 'splatplost/splatplan'],
        package_dir={'splatplost': 'splatplost'},
        packages=find_packages(),
        url='https://github.com/Victrid/splatplost',
        license='GPLv3',
        author='Weihao Jiang',
        author_email='weihau.chiang@gmail.com',
        description='A software-based SplatPost plotter.',
        install_requires=[
            "numpy~=1.23.2",
            "Pillow~=9.2.0",
            "setuptools~=65.3.0",
            "scipy~=1.9.1",
            "tqdm~=4.64.0",
            "scikit-image~=0.19.3",
            "dbus-python~=1.2.18",
            "libnxctrl~=0.1.1",
            ]
        )

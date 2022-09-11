from pathlib import Path

from setuptools import find_packages, setup

this_directory = Path(__file__).parent
long_description = (this_directory / "readme.md").read_text()

exec(open("splatplost/version.py").read())

# noinspection PyUnresolvedReferences
version = __version__

from setuptools.command.build_py import build_py as _build_py


class LangBuilder(_build_py):
    def get_translation(self):
        import glob
        from subprocess import run
        result = []
        ts_files = glob.glob(str(Path(__file__).parent / Path("splatplost/gui/i18n") / "*.ts"))
        for ts_file in ts_files:
            qm_file = ts_file.replace(".ts", ".qm")
            run(["lrelease", ts_file, "-qm", qm_file])
            result.append(qm_file)
        return result

    def run(self):
        self.get_translation()
        super().run()


setup(name='splatplost',
      version=version,
      scripts=['splatplost/gui/splatplost'],
      package_dir={'splatplost': 'splatplost'},
      packages=find_packages(exclude=['test']),
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
      cmdclass={
          "build_py": LangBuilder,
          },
      install_requires=[
          "numpy~=1.23.2",
          "Pillow~=9.2.0",
          "setuptools~=65.3.0",
          "scipy~=1.9.1",
          "tqdm~=4.64.0",
          "scikit-image~=0.19.3",
          "libnxctrl~=0.1.7",
          "tsp-solver2~=0.4.1",
          "PyQt6~=6.3.1"],
      python_requires=">=3.10",
      package_data={"splatplost": [
          "gui/*.ui",
          "gui/i18n/*.ts",
          "gui/i18n/*.qm"
          ]}, )

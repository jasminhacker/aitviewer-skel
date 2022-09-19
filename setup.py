from setuptools import setup, find_packages
from aitviewer import __version__

setup(name='aitviewer',
      description='Viewing and rendering of sequences of 3D data.',
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      url="https://github.com/eth-ait/aitviewer",
      version=__version__,
      author='Manuel Kaufmann, Velko Vechev, Dario Mylonopoulos',
      packages=find_packages(),
      include_package_data=True,
      keywords=['viewer', 'moderngl', 'machine learning', 'sequences', 'smpl', 'computer graphics', 'computer vision',
                '3D', 'meshes', 'visualization'],
      platforms=['any'],
      python_requires='>=3.7',
      install_requires=[
              'torch>=1.6.0',
              'numpy>=1.18,<2',
              'opencv-contrib-python-headless>=4.5.1.48',
              'smplx',
              'moderngl-window>=2.4.0',
              'moderngl>=5.6.4,<6.0',
              'PyQt5>=5.15.4',
              'imgui>=1.3.0',
              'tqdm>=4.60.0',
              'trimesh>=3.9.15,<4',
              'rtree>=0.9.7',
              'scipy>=1.5.2,<1.8',
              'omegaconf>=2.1.1',
              'roma>=1.2.3',
              'joblib',
              'scikit-video',
              'Pillow'
          ])

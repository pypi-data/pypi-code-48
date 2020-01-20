from setuptools import setup
import glob, os

web = []
for root, subdirs, files in os.walk(os.path.join('wordmap')):
  if not files: continue
  for file in files:
    web.append(os.path.join(root.replace('wordmap/', ''), file))

setup (
  name='wordmap',
  version='0.1.3',
  packages=['wordmap'],
  package_data={
    'wordmap': web,
  },
  keywords = ['webgl', 'three.js', 'word2vec', 'tsne', 'umap', 'machine-learning'],
  description='Visualize massive word collections',
  url='https://github.com/yaledhlab/wordmap',
  author='Douglas Duhaime',
  author_email='douglas.duhaime@gmail.com',
  license='MIT',
  install_requires=[
    'Flask>=0.12.2',
    'Flask-Cors>=3.0.3',
    'gensim>=3.6.0',
    'glob2>=0.6',
    'gunicorn>=19.7.1',
    'ivis>=1.2.3',
    'joblib>=0.13.2',
    'lloyd>=0.0.7',
    'matplotlib>=2.0.0',
    'numpy>=1.15.1',
    'PyWavefront>=1.0.5',
    'scikit-learn>=0.21.2',
    'scipy==1.1.0',
    'umap-learn>=0.3.8',
    'yale_dhlab_rasterfairy>=1.0.3',
    'vertices==0.0.5',
    'tensorflow==1.15.0'
  ],
  entry_points={
    'console_scripts': [
      'wordmap=wordmap:parse',
    ],
  },
)

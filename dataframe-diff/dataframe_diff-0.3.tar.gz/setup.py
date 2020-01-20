from distutils.core import setup
setup(
  name = 'dataframe_diff',         # How you named your package folder (MyLib)
  packages = ['dataframe_diff'],   # Chose the same as "name"
  version = '0.3' ,    # Start with a small number and increase it with every change you make
  license='MIT',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'Compare two dataframes and return column-wise difference and additional record',   # Give a short description about your library
  long_description = """Compare two dataframes and return column-wise difference and additional record""",
  author = 'Aditya Yogi',                   # Type in your name
  author_email = 'adityayoginiet@gmail.com',      # Type in your E-Mail
  url = 'https://github.com/yogiadi/dataframe_diff',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/yogiadi/pd_df_compare/archive/v_03.tar.gz',    # I explain this later on
  keywords = ['pandas', 'dataframe', 'compare', 'dataframe_diff','dataframe difference'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'pandas',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',      # Define that your audience are developers
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',   # Again, pick a license
    'Programming Language :: Python :: 3',      #Specify which pyhton versions that you want to support
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
  ],
)

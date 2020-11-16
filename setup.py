from setuptools import setup, find_packages

setup(name='calgem_scraper',
      version='0.0.1',
      description='Scrape pdf and header data from calgem',
      url='https://github.com/hasunhkhan/Calgem_Scraper',
      author='Hasun Khan',
      author_email='',
      license='MIT',
      packages=find_packages(),
      install_requires=[  # 'cx_Oracle',
          # 'pandas',
          'boto3',
          'beautifulsoup4',
      ],
      zip_safe=True,
      test_suite='nose.collector',
      tests_require=['nose'],
      # package_data={'crcdal': [
      #     'packageData/*.csv',
      #     'packageData/*.pkl',
      #     'packageData/*.yaml',
      #     'packageData/configurations/*.yaml',
      #     'packageData/forecast_model_dictionary/*.yaml',
      #     'packageData/database_name_cleaner_tables/*.csv']}
      )

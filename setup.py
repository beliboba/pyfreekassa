from setuptools import setup, find_packages


with open('./README.md', 'r') as f:
	readme = f.read()

setup(
	name='pyfreekassa',
	version='1.0.1',
	description='Python wrapper for FreeKassa api',
	long_description=readme,
	long_description_content_type='text/markdown',
	url='https://github.com/beliboba/pyfreekassa',
	author='Beliboba',
	author_email='belibobka@gmail.com',

	keywords=['freekassa', 'api', 'wrapper', 'client', 'sdk'],

	packages=find_packages(exclude=['tests', 'docs']),

	install_requires=['aiofiles', 'aiohttp'],

	python_requires='>3.6',

	project_urls={
		'Source': 'https://github.com/beliboba/pyfreekassa'
	}
)
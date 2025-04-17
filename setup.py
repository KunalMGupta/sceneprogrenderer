from setuptools import setup, find_packages
setup(
    name='sceneprogrenderer',  # Replace with your package's name
    version='0.1.2',    # Replace with your package's version
    description='A Renderer built for the SceneProg project',  # Replace with a short description of your package
    long_description=open('README.md').read(),  # Optional: Use your README for a detailed description
    long_description_content_type='text/markdown',
    author='Kunal Gupta',
    author_email='k5upta@ucsd.edu',
    url='https://github.com/KunalMGupta/sceneprogrenderer.git',  # Optional: Replace with your repo URL
    packages=find_packages(),  # Automatically find all packages in your project
    include_package_data=True,  # Include non-code files specified in MANIFEST.in
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',  # Replace with the minimum Python version your package supports
)
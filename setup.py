import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="superwand",
    version="0.1.4",
    author="Julian Henry",
    description="A tool for retheming images and CSS using color palettes and gradients.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/juleshenry/superwand",
    project_urls={
        "Bug Tracker": "https://github.com/juleshenry/superwand/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "numpy",
        "pillow",
        "scipy",
        "matplotlib",
        "scikit-learn",
        "flask",
        "werkzeug",
    ],
    extras_require={
        "test": ["pytest", "pytest-cov"],
    },
    include_package_data=True,
    package_data={
        "superwand": [
            "assets/fonts/*.ttf",
            "assets/themes_jpgs/*.jpg",
            "studio/templates/*.html",
            "studio/static/**/*",
        ],
    },
    entry_points={
        "console_scripts": [
            "superwand = superwand.core.superwand:main",
            "gradient-enforce = superwand.utils.gradient_enforce:main",
        ],
    },
)

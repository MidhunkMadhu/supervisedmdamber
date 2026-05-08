from setuptools import setup

setup(
    name="supervisedmdamber",
    version="1.0.0",
    py_modules=["supervisedmdamber"],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "supervisedmdamber=supervisedmdamber:main",
        ],
    },
)

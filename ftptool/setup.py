from distutils.core import setup
import os

readme_fname = os.path.join(os.path.dirname(__file__), "README.rst")
readme_text = open(readme_fname).read()

setup(name="ftptool", version="1.1.0",
      url="",
      description="Higher-level interface to ftplib",
      author="Jinzhouyun",
      author_email="2435575291@qq.com",
      requires=["six"],
      long_description=readme_text,
      py_modules=["ftptool"])

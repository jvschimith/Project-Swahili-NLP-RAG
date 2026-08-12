"""
Setup configuration for Swahili NLP RAG
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="swahili-nlp-rag",
    version="v2.1.1-alpha",
    author="Your Name",
    author_email="your.email@example.com",
    description="Internal/local alpha release of the Swahili linguistic intelligence repository",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/swahili-nlp-rag",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: Swahili",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.9",
    install_requires=[
        "python-dotenv>=1.0.0",
        "pydantic>=2.5.3",
        "pydantic-settings>=2.1.0",
        "loguru>=0.7.2",
        "SQLAlchemy>=2.0.23",
        "pandas>=2.1.4",
        "numpy>=1.26.2",
        "click>=8.1.7",
        "tqdm>=4.66.1",
        "rich>=13.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "black>=23.12.1",
            "isort>=5.13.2",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
        ],
        "web": [
            "fastapi>=0.109.0",
            "uvicorn>=0.26.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "swahili-nlp=src.cli:main",
        ],
    },
)

"""
Setup configuration for Swahili NLP RAG v2.1
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="swahili-nlp-rag",
    version="2.1.0",
    author="Swahili NLP Contributors",
    author_email="contact@example.com",
    description="Comprehensive NLP system for Swahili with morphological analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/swahili-nlp-rag",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: Swahili",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.10",
    install_requires=[
        # Core dependencies
        "python-dotenv>=1.0.0",
        "pydantic>=2.5.3",
        "pydantic-settings>=2.1.0",
        "loguru>=0.7.2",
        
        # Database
        "SQLAlchemy>=2.0.23",
        "alembic>=1.13.1",
        
        # Data processing
        "pandas>=2.1.4",
        "numpy>=1.26.2",
        
        # Web & API
        "fastapi>=0.109.0",
        "uvicorn[standard]>=0.26.0",
        "python-multipart>=0.0.6",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.2",
        
        # ML & Research
        "scikit-learn>=1.3.2",
        "datasets>=2.16.1",
        "transformers>=4.36.2",
        "torch>=2.1.2",
        
        # Translation
        "googletrans==4.0.0rc1",
        
        # Visualization
        "streamlit>=1.31.0",
        "plotly>=5.18.0",
        
        # Utilities
        "click>=8.1.7",
        "tqdm>=4.66.1",
        "rich>=13.7.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "black>=23.12.1",
            "isort>=5.13.2",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
            "ipython>=8.19.0",
            "jupyter>=1.0.0",
        ],
    },
    # No CLI entry point - use API or Dashboard
)

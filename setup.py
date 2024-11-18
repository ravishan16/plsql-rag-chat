from setuptools import setup, find_packages

setup(
    name="plsql_rag_chat",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.30.0",
        "langchain>=0.1.0",
        "langchain-community>=0.0.10",
        "faiss-cpu>=1.7.4",
        "python-dotenv>=1.0.0",
        "boto3>=1.34.0",
        "requests>=2.31.0",
        "numpy>=1.26.0",
        "sqlparse>=0.4.4",
    ],
    python_requires=">=3.8",
)
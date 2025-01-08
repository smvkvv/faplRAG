# fapl RAG

Content for project is based on data from resource: **https://fapl.ru**

Repository structure
------------

    ├── README.md                   <- project description
    │
    ├── experiments                 <- jupyter notebooks with experiments
    │
    ├── airlfow_local               <- airflow
    │
    ├── data                        <- extension for vector database
    │
    ├── interface                   <- future backend of the service
    |
    ├── utils                       <- some database and airlow utils scripts
    │
    └── requirements.txt            <- requirements

--------

## How to run the project

1. Clone the repository:

    git clone <repository_url>
    cd <repository_directory>

2. Configure your embedder:

At interface/config.yaml set values for parameters for embedding model.

File interface/config.yaml lets you change the experimental parameters. 

 
3. Setup the project:

For project preparation we must load some data via airflow:

    make setup

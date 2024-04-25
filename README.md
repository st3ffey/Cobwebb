# Cobwebb

Cobwebb is a project that allows users to chat against financial proxies from S&P 500 companies. It is comprehensive, meaning:

-- It scrapes the data from publicly available websites
---- It aquires the current list of S&P 500 companies from a wikipedia article
---- It uses this list of companies to sift through the sec edgar website and extract raw information from the html sites.

-- The documents, in their raw form, are embedded, and the embeddings are stored in a cloud-based vector store.

-- The pipeline for prompting is the main bit of the backend

-- The application is currently hosted on [www.cobwebb.pythonanywhere.com](https://cobwebb.pythonanywhere.com/), using the frontend source code here. Not available to the public yet, but if you want to try out the application for yourself, you can clone this repo and run locally.

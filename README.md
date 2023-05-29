# Starlink GraphQL API

This project provides a GraphQL API to query the last known position of Starlink satellites and find the closest satellite to a given position at a specific time. It utilizes a PostgreSQL database to store and retrieve the satellite data.

## Installation

1. Start the Docker containers:

   ```
   docker-compose up -d
   ```I apologize for missing that part. Here's the updated section for the Usage part of the readme:

## Usage

1. Check the logs and find the message of the import script.

   ```
   $ docker logs blueonion-import-script-1
   INFO:__main__:Inserted 3141 records into the database.
   INFO:__main__:Database connection closed.
   blueonion-import-script-1 exited with code 0
   ```

2. Go to `localhost:5000/graphql` and query the available fields and perform queries. Here are some example queries:

   - Query the last known position of a satellite:

     ```graphql
     query {
       lastKnownPosition(satelliteId: "2020-012AC") {
         id
         longitude
         latitude
       }
     }
     ```

   - Find the closest satellite to a given position at a specific time:

     ```graphql
     query {
       closestSatellite(latitude: 40.7128, longitude: -74.0060, timestamp: "2023-05-28T12:00:00Z") {
         id
         longitude
         latitude
         distance
       }
     }
     ```

## Database Folder Explanation

The `database` folder contains the following files:

- `import_data.py`: This Python script is responsible for importing the Starlink historical data into the PostgreSQL database. It connects to the database, reads the data from the `starlink_historical_data.json` file, and inserts it into the `starlink_positions` table.

- `entrypoint/init.sql`: This SQL script is executed when the PostgreSQL container starts. It contains the necessary schema definition and table creation statements for the `starlink_positions` table.

- `postgres.py`: This Python module defines the `PostgreSQL` class, which handles the connection, disconnection, and querying of the PostgreSQL database. It provides methods for inserting starlink data, querying the last known position, and getting the closest satellite.

- `starlink_historical_data.json`: This JSON file contains the historical data of Starlink satellites. It is read by the `import_data.py` script to populate the database.

The `database` folder is responsible for managing the database-related functionality, including the PostgreSQL database connection, data import, and query operations.

## GQL Folder

The `gql` folder contains the following files:

- `app.py`: This Python script is responsible for starting the Flask application and configuring the GraphQL endpoint. It creates a Flask app instance and registers the GraphQL endpoint using the `schema` defined in `schema.py`.

- `schema.py`: This Python module defines the GraphQL schema using the `graphene` library. It includes the definition of the `StarlinkPosition` and `ClosestSatellite` GraphQL object types, as well as the `Query` object type. The `Query` object type defines the available queries, including `lastKnownPosition` and `closestSatellite`. Each query has its corresponding resolver method defined in the `Query` class.

The `gql` folder is responsible for handling the GraphQL functionality of the application. It defines the GraphQL schema and provides the resolvers for the defined queries. The `app.py` script starts the Flask application and exposes the GraphQL endpoint for querying the data.

## Docker-compose Explanation

The `docker-compose.yaml` file defines three services: `postgres`, `import-script`, and `graphql-api`. Here's a breakdown of each service:

- `postgres`: This service uses the `postgres:latest` image and maps the container's port 5432 to the host's port 5432.

- `import-script`: This service builds an image using the Dockerfile in the current context. It depends on the `postgres` service, so it will start after the `postgres` service is up and running. The `environment` section inherits the environment variables from the `postgres` service using the `<<: *postgres-common-env` notation. The `entrypoint` specifies the command to be executed when the container starts, which is running the `import_data.py` script.

- `graphql-api`: This service also builds an image using the Dockerfile in the current context. It depends on the `import-script` service, so it will start after the `import-script` service is up and running. The `ports` section maps the container's port 5000 to the host's port 5000, allowing access to the GraphQL API. The `environment` section inherits the environment variables from the `postgres` service.

## TODO List

- [ ] Implement a data retrieval handler to fetch the latest data from the API and update the PostgreSQL database accordingly.
- [ ] Create unit tests to ensure the correctness of the implemented functionality.
- [ ] Implement error handling and exception handling mechanisms to handle potential errors and exceptions gracefully.
- [ ] Add logging statements or integrate a logging framework to log important events and error messages.
- [ ] Implement a periodic task or a scheduler to automatically fetch and update the data from the API at regular intervals.
- [ ] Consider implementing caching mechanisms to improve performance and reduce the number of API calls.

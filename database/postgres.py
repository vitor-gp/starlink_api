import os
from typing import Dict, Optional, Union, List, Tuple
from datetime import datetime

import psycopg2
from haversine import haversine, Unit


class PostgreSQLConnection:
    def __init__(self):
        """
        Initializes a PostgreSQL connection object.

        Reads the PostgreSQL connection details from environment variables.
        """
        self.host = os.environ.get('POSTGRES_HOST')
        self.port = os.environ.get('POSTGRES_PORT')
        self.database = os.environ.get('POSTGRES_DB')
        self.user = os.environ.get('POSTGRES_USER')
        self.password = os.environ.get('POSTGRES_PASSWORD')
        self.connection = None
        self.cursor = None

    def __enter__(self):
        """
        Enters the context and establishes a connection to the PostgreSQL database.
        """
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exits the context and closes the connection to the PostgreSQL database.
        """
        self.disconnect()

    def connect(self):
        """
        Establishes a connection to the PostgreSQL database.
        """
        self.connection = psycopg2.connect(
            host=self.host,
            port=self.port,
            database=self.database,
            user=self.user,
            password=self.password
        )
        self.cursor = self.connection.cursor()

    def commit(self):
        """
        Commits the changes made in the current transaction.
        """
        self.connection.commit()

    def disconnect(self):
        """
        Closes the connection to the PostgreSQL database.
        """
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()


class PostgreSQLDataHandler:
    def __init__(self, connection: PostgreSQLConnection):
        """
        Initializes a PostgreSQL data handler object.

        Args:
            connection (PostgreSQLConnection): The PostgreSQL connection object.
        """
        self.connection = connection


    def insert_starlink_data(self, records: List[Tuple[str, str, float, float]]) -> None:
        """
        Inserts multiple starlink data records into the starlink_positions table.

        Args:
            records (List[Tuple[str, str, float, float]]): The list of records to insert.
                Each record is a tuple containing satellite_id, creation_date, longitude, and latitude.
        """
        with self.connection:
            self.connection.cursor.executemany(
                """
                INSERT INTO starlink_positions (id, creation_date, longitude, latitude)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id, creation_date) DO NOTHING
                """,
                records
            )
            self.connection.commit()
            

    def query_last_known_position(self, satellite_id: str) -> Optional[Dict[str, Union[float, None]]]:
        """
        Queries the last known position of a satellite.

        Args:
            satellite_id (str): The ID of the satellite.

        Returns:
            dict: The last known position, including longitude and latitude.
                  Returns None if no position is found.
        """
        with self.connection:
            self.connection.cursor.execute(
                """
                SELECT longitude, latitude
                FROM starlink_positions
                WHERE id = %s
                ORDER BY creation_date DESC
                LIMIT 1
                """,
                (satellite_id,)
            )
            result = self.connection.cursor.fetchone()
            if result:
                return {
                    'longitude': result[0],
                    'latitude': result[1]
                }
            return None

    def get_closest_satellite(self, latitude: float, longitude: float, timestamp: datetime) -> Optional[Dict[str, Union[str, float]]]:
        """
        Retrieves the closest satellite to a given position at a specific timestamp.

        Args:
            latitude (float): The latitude of the given position.
            longitude (float): The longitude of the given position.
            timestamp (datetime.datetime): The specific timestamp to find the closest satellite.

        Returns:
            dict: The closest satellite ID and its distance to the given position.
                  Returns None if no satellite is found.
        """
        with self.connection:
            self.connection.cursor.execute("""
                SELECT DISTINCT ON (id) id, latitude, longitude
                FROM starlink_positions
                WHERE creation_date <= %s AND latitude <> 0 AND longitude <> 0
                ORDER BY id, creation_date DESC
            """, (timestamp,))
            rows = self.connection.cursor.fetchall()

            closest_distance = None
            closest_satellite = None

            for row in rows:
                satellite_id, satellite_latitude, satellite_longitude = row
                satellite_coordinates = (satellite_latitude, satellite_longitude)
                given_coordinates = (latitude, longitude)
                distance = haversine(given_coordinates, satellite_coordinates, unit=Unit.METERS)
                if closest_distance is None or distance < closest_distance:
                    closest_distance = distance
                    closest_satellite = {
                        'id': satellite_id,
                        'latitude': satellite_latitude,
                        'longitude': satellite_longitude,
                        'distance': closest_distance,
                    }

            return closest_satellite

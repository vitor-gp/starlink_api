from datetime import datetime
from typing import Optional

import graphene
from graphene.types.datetime import DateTime

from database.postgres import PostgreSQLConnection, PostgreSQLDataHandler


class StarlinkPosition(graphene.ObjectType):
    """
    GraphQL Object Type representing the last known position of a satellite.
    """
    id = graphene.String()
    longitude = graphene.Float()
    latitude = graphene.Float()


class ClosestSatellite(graphene.ObjectType):
    """
    GraphQL Object Type representing the closest satellite to a given position at a specific time.
    """
    id = graphene.String()
    longitude = graphene.Float()
    latitude = graphene.Float()
    distance = graphene.Float()


class Query(graphene.ObjectType):
    """
    GraphQL Query class defining the available queries.
    """
    last_known_position = graphene.Field(
        StarlinkPosition,
        satellite_id=graphene.String(required=True, description="The ID of the satellite.")
    )

    closest_satellite = graphene.Field(
        ClosestSatellite,
        latitude=graphene.Float(required=True, description="The latitude of the given position."),
        longitude=graphene.Float(required=True, description="The longitude of the given position."),
        timestamp=DateTime(required=True, description="The timestamp to find the closest satellite.")
    )

    def resolve_last_known_position(self, info, satellite_id: str) -> Optional[StarlinkPosition]:
        """
        Resolves the last known position query.

        Args:
            info (graphql.execution.base.ResolveInfo): Information about the query execution.
            satellite_id (str): The ID of the satellite.

        Returns:
            Optional[StarlinkPosition]: The last known position of the satellite.
                                        Returns None if no position is found.
        """
        with PostgreSQLConnection() as connection:
            data_handler = PostgreSQLDataHandler(connection)
            result = data_handler.query_last_known_position(satellite_id)

            if result:
                return StarlinkPosition(
                    id=satellite_id,
                    longitude=result['longitude'],
                    latitude=result['latitude']
                )
            return None

    def resolve_closest_satellite(self, info, latitude: float, longitude: float, timestamp: datetime) -> Optional[ClosestSatellite]:
        """
        Resolves the closest satellite query.

        Args:
            info (graphql.execution.base.ResolveInfo): Information about the query execution.
            latitude (float): The latitude of the given position.
            longitude (float): The longitude of the given position.
            timestamp (datetime.datetime): The timestamp to find the closest satellite.

        Returns:
            Optional[ClosestSatellite]: The closest satellite to the given position at the given timestamp.
                                        Returns None if no satellite is found.
        """
        with PostgreSQLConnection() as connection:
            data_handler = PostgreSQLDataHandler(connection)
            closest_satellite = data_handler.get_closest_satellite(latitude, longitude, timestamp)

            if closest_satellite:
                return ClosestSatellite(
                    id=closest_satellite['id'],
                    longitude=closest_satellite['longitude'],
                    latitude=closest_satellite['latitude'],
                    distance=closest_satellite['distance']
                )
            return None


schema = graphene.Schema(query=Query)

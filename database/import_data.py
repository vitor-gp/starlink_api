import ijson
import logging

from postgres import PostgreSQLDataHandler, PostgreSQLConnection

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Read the starlink_historical_data.json file
with open('database/data/starlink_historical_data.json', 'rb') as json_file:
    # Import the starlink data into the database
    with PostgreSQLConnection() as connection:
        data_handler = PostgreSQLDataHandler(connection)

        # Prepare the batch insert data
        batch_size = 5000  # Adjust batch size as needed
        records = []

        # Iterate over the JSON file using ijson
        parser = ijson.parse(json_file)
        for prefix, event, value in parser:
            if prefix == 'item.spaceTrack.OBJECT_ID':
                satellite_id = value
            elif prefix == 'item.spaceTrack.EPOCH':
                creation_date = value
            elif prefix == 'item.longitude':
                longitude = value
            elif prefix == 'item.latitude':
                latitude = value
                # Append the record to the batch
                records.append((satellite_id, creation_date, longitude, latitude))

                # Perform batch insertion when the batch size is reached
                if len(records) >= batch_size:
                    data_handler.insert_starlink_data(records)
                    logger.info(f'Inserted {len(records)} records into the database.')
                    records = []

        # Insert any remaining records in the last batch
        if records:
            data_handler.insert_starlink_data(records)
            logger.info(f'Inserted {len(records)} records into the database.')

        logger.info('Database connection closed.')

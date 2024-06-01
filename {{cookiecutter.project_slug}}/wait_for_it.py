import sys
import time

import psycopg2
from decouple import config


def check_database():
    db_params = {
        'host': config('POSTGRES_HOST'),
        'port': config('POSTGRES_PORT'),
        'user': config('POSTGRES_USER'),
        'password': config('POSTGRES_PASSWORD'),
        'database': config('POSTGRES_NAME'),
    }

    max_attempts = 10
    delay = 5

    for attempt in range(1, max_attempts + 1):
        try:
            conn = psycopg2.connect(**db_params)
            conn.close()
            print(f"Successfully connected to the database on attempt {attempt}.")
            sys.stdout.flush()
            return True
        except psycopg2.OperationalError as e:

            print(f"Attempt {attempt}: Database not ready yet: {e}")
            sys.stdout.flush()
            if attempt < max_attempts:
                time.sleep(delay)

    print("Exceeded maximum attempts. Unable to connect to the database.")
    return False


if __name__ == "__main__":
    if check_database():
        print("Database is ready! Starting your Django API container...")
        sys.stdout.flush()
        # Replace this line with the command to start your Django API container.
    else:
        print("Django API container will not start.")

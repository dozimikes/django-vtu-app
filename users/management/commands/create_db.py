from django.core.management.base import BaseCommand
import psycopg2
from psycopg2 import sql

class Command(BaseCommand):
    help = "Create the PostgreSQL database"

    def handle(self, *args, **kwargs):
        connection = psycopg2.connect(
            dbname="lextrol_db",
            user="",
            password="",
            host="localhost",
            port="5432"
        )
        connection.autocommit = True
        cursor = connection.cursor()
        database_name = "irecharge_db"
        try:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(database_name)))
            self.stdout.write(self.style.SUCCESS(f"Database '{database_name}' created successfully."))
        except psycopg2.errors.DuplicateDatabase:
            self.stdout.write(self.style.WARNING(f"Database '{database_name}' already exists."))
        finally:
            cursor.close()
            connection.close()

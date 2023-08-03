#!/usr/bin/env python
"""
    Main filter file
"""
import logging
import re

import os
# import mysql.connector


def get_db():
    """filter datnum function"""
    username = os.environ.get("PERSONAL_DATA_DB_USERNAME", "root")
    password = os.environ.get("PERSONAL_DATA_DB_PASSWORD", "")
    host = os.environ.get("PERSONAL_DATA_DB_HOST", "localhost")
    db_name = os.environ.get("PERSONAL_DATA_DB_NAME")

    db_connection = mysql.connector.connect(
        user=username,
        password=password,
        host=host,
        database=db_name
    )

    return db_connection


def filter_datum(fields, redaction, message, separator):
    """filter datnum function"""
    for field in fields:
        message =\
            re.sub(
                r'(?<=\b' + field + r'=' + r')([^' + separator + r']*)',
                redaction, message)
    return message


class RedactingFormatter(logging.Formatter):
    """ Redacting Formatter class """

    REDACTION = "***"
    FORMAT = "[HOLBERTON] %(name)s %(levelname)s %(asctime)-15s: %(message)s"
    SEPARATOR = ";"

    def __init__(self, fields: list):
        """filter datnum function"""
        super(RedactingFormatter, self).__init__(self.FORMAT)
        self.fields = fields

    def format(self, record: logging.LogRecord) -> str:
        """filter datnum function"""
        record.msg =\
            filter_datum(self.fields, self.REDACTION,
                         record.msg, self.SEPARATOR)
        return super(RedactingFormatter, self).format(record)


PII_FIELDS = ("name", "email", "ssn", "password", "credit_card")


def get_logger() -> logging.Logger:
    """filter datnum function"""
    logger = logging.getLogger("user_data")
    logger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    formatter = RedactingFormatter(fields=PII_FIELDS)
    stream_handler.setFormatter(formatter)

    logger.addHandler(stream_handler)
    logger.propagate = False

    return logger

import pymysql

# Install PyMySQL as MySQLdb
pymysql.install_as_MySQLdb()

# Patch version info to satisfy Django's mysqlclient version check
# Django 6.x requires mysqlclient >= 2.2.1, but PyMySQL 1.4.6 reports as 1.4.6
import MySQLdb as Database

Database.version_info = (2, 2, 4, 'final', 0)
# Some Django versions use __version__ (string) in the error message
Database.__version__ = '2.2.4'



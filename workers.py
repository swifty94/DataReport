import logging.config
import logging
logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
import mysql.connector
from multiprocessing import Process
import os, csv, os.path
import sqlite3

class MySQLProcessor():
    """
    \n Class for creation mysql.connector cursor
    \n Parsing the result of mysql fetchall() method to list instead of tuple + trim unwanted chars    
    """    
    def fetch_result(self,query):
        """
        \n Method accepting SQL query as a param to process (Defined in settings.py)
        \n Return: list of results
        """
        try:            
            from settings import MYSQL_DBCONFIG            
            connection = mysql.connector.connect(**MYSQL_DBCONFIG)
            cursor = connection.cursor()
            cursor.execute(query)
            result = cursor.fetchall()
            final = []
            for param in result:
                param = str(param)
                param = param.strip('(,)')
                final.append(param)
            return final
        except mysql.connector.errors.InterfaceError as c:
            _l = f'Cannot connect to MySQL database! {c}. Application exit!'
            logging.critical(_l)
            print(_l)
            exit(1)
        except Exception as e:
            logging.error(f'{self.__class__.__name__ } error {e}')
            logging.debug(f'{self.__class__.__name__ } SQL: \n {query}')
            if cursor and connection:
                cursor.close()
                connection.close()
        finally:                            
            if cursor and connection:
                cursor.close()
                connection.close()                


class SQLLiteProcessor():

    @staticmethod
    def isDb() -> bool:            
        """
        :Check if DB exists \n
        :Accept - None\n
        :Return - Bool
        """
        try:                        
            db = os.path.isfile('cpe.db')
            if db:
                logging.info(f'{__class__.__name__ } Internal database already exist')
                logging.info(f'{__class__.__name__ } Re-creating application schema')
                os.remove('cpe.db') 
                SQLLiteProcessor.initDb()                     
                return True
            else:
                logging.info(f'{__class__.__name__ } Internal database does not exist')
                logging.info(f'{__class__.__name__ } Creating application schema')
                SQLLiteProcessor.initDb()      
                return False
        except PermissionError as p:
            _l = f"Cannot access internal database: {p}"
            logging.critical(_l)
            print(_l)
            exit(1)
        except Exception as e:            
            logging.error(f'{__class__.__name__ } Error \n{e}', exc_info=1)
    
    @staticmethod
    def connect():
        """
        :Creating SQLite connection \n
        :Accept - None\n
        :Return - Connection object
        """
        try:
            connection = sqlite3.connect('cpe.db')            
            return connection
        except sqlite3.Error as e:
            logging.error(f'{__class__.__name__ } Error \n{e}', exc_info=1)
    
    @staticmethod
    def initDb():
        """
        :Initiating database if not exist \n
        :Accept - None\n
        :Return - None
        """
        try:                        
            connection = None                         
            connection = SQLLiteProcessor.connect()
            cursor = connection.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS `cpeModel` (
            `ID`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            `cpe_id`	INTEGER,
            `serial`	TEXT,
            `manufacturer`	TEXT,
            `modelname`	TEXT,
            `activeip`	TEXT,
            `wanusername`	TEXT,
            `connectiontype`	TEXT,
            `modulation`	TEXT,
            `activeconnection`	TEXT,
            `updated`	TEXT);
            """)
        except Exception as e:
            logging.error(f'{__class__.__name__ } Error \n{e}', exc_info=1)
        finally:
            connection.commit()                        
            logging.info(f'{__class__.__name__ } Database created')
            if connection:
                connection.close()

    @staticmethod
    def insert_data(json):
        """
        Connect to DB instance and perform INSERT
        """
        try:            
            connection = sqlite3.connect('cpe.db')
            cursor = connection.cursor()        
            sql = """
            INSERT or IGNORE INTO cpeModel
            (cpe_id, serial, manufacturer, modelname, activeip, wanusername, connectiontype, modulation, activeconnection, updated) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
            data = []
            for value in json.values():
                    data.append(value)
            data = tuple(data)            
            cursor.execute(sql, data)
            connection.commit()
            if cursor.lastrowid:
                logging.info(f'{__class__.__name__ } InsertedID - {cursor.lastrowid}')
                cursor.close()            
        except sqlite3.Error as e:
            logging.error(f'{__class__.__name__ } Error {e} \n With ID {cursor.lastrowid}')
            logging.error(f'{__class__.__name__ } SQL: {sql}')
            logging.error(f'{__class__.__name__ } Data: {data}')
            cursor.close()
        finally:
            if (connection):
                connection.close()                

    @staticmethod
    def select_data(sql):
        """
        Connect to DB instance and perform SELECT
        """    
        try:
            connection = sqlite3.connect('cpe.db')
            cursor = connection.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()
            if result:
                logging.info(f'{__class__.__name__ } cpeModel queried')                
                cursor.close()            
                return result
        except Exception as e:
            logging.error(f"{__class__.__name__ } cpeModel query failed with exception \n {e} \n ")
            logging.error(f'{__class__.__name__ } SQL: \n {sql} \n ')
        finally:
            if (connection):
                connection.close()

class CSVWritter():
    """
    Class with a single method to create CSV report
    Accepting keys [header of report], report_name [csv file name], json [data to be written as dict]
    """
    @staticmethod
    def write_to_csv(keys,report_name,json):        
        try:            
            exist = os.path.isfile(report_name)
            with open(report_name, 'a', newline='') as csvfile:
                writer = csv.DictWriter(csvfile, delimiter=',', lineterminator='\r\n', fieldnames=keys)
                if not exist:
                    writer.writeheader()
                writer.writerow(json)
        except FileNotFoundError:
            logging.critical(f"\nCant access either reports/ folder or destination file {report_name}.")
            print(f"\nCant access either \"reports/\" folder or destination file {report_name}.")
            return
        except Exception as e:
            logging.error(f'{__class__.__name__ } CSV data processing error {e}',exc_info=1)        
            

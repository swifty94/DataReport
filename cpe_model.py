import os, re, csv, time
import datetime
from time import time
from multiprocessing import Process
import logging.config
import logging
logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
from workers import SQLLiteProcessor, MySQLProcessor, CSVWritter

class CPEModel():
    """
    \n Class with methods working over CPE data in FT DB:
    \n >>> get_ids() -> Accepting None -> Return iterable list of CPE ids     
    \n >>> process_device_data() -> Accepting None -> Return Process instance of SQLLiteProcessor class method to save data into inner app DB
    \n >>> report() -> Accepting report_type (str) -> Return Process instance of CSVWritter class method to write requested data to CSV    
    \n >>> getcpe_by_un() -> Accepting file name to process (str) -> Return - Return Process instance of CSVWritter class method to write requested data to CSV    
    """    
    @staticmethod
    def get_ids():
        try:            
            Processor = MySQLProcessor()            
        except Exception as e:
            logging.error(f'{__class__.__name__ } failed to instantiate {MySQLProcessor.__class__.__name__}, error {e}, Full trace: \n', exc_info=1)
        finally:
            if Processor:
                logging.info(f'{__class__.__name__ } New instance {Processor.__class__.__name__} created')
                                    
        try:
            ids_list = Processor.fetch_result("select id from cpe")
            return ids_list
        except Exception as e:
            logging.error(f'{__class__.__name__ } error {e}',exc_info=1)
        finally:
            if ids_list:
                logging.info(f'{__class__.__name__ } Result fetched')                
            else:
                logging.error(f'{__class__.__name__ } Result fetch FAILED')            
    
    @staticmethod
    def process_device_data():
        """
        \n Method processing CPE data and collecting it into array of arrays 
        \n Each subarray is a single CPE model
        \n Return: Process-ID of any worker that can process incomming data in JSON
        """
        try:
            logging.info(f'{__class__.__name__ } Result fetch start')
            Processor = MySQLProcessor()            
        except Exception as e:
            logging.error(f'{__class__.__name__ } failed to instantiate {MySQLProcessor.__class__.__name__}')
            logging.error(f'{__class__.__name__ } error {e}',exc_info=1)
        finally:            
            if Processor:
                logging.info(f'{__class__.__name__ } new object of {Processor.__class__.__name__} created')
            
        #
        #   Here comes a kind of tricky alhorithm of building CPE data model
        #
        #   {
        #   id                  INT,        Main search key
        #   serial              STR,        Serials based on CPE ID + table constraints
        #   manufaturer         STR,        Manufactureres based on CPE ID + table constraint
        #   modelname           STR,        Models based on CPE ID + table constraint
        #   activeips           STR,        Active IP based on CPE ID + table constraint
        #   activeconnection,   STR,        Active connection based on CPE ID + Active IP + TR object pattern match
        #   connectiontype,     STR,        CPE connection type based on CPE ID + Active connection object + TR object pattern match
        #   wanusername         STR         WAN username (if exists) based on CPE ID + Active connection object + TR object pattern match
        #    }
        #
        #
        logging.info(f'{__class__.__name__ } Result fetch start')
        try:            
            from settings import SERIAL_Q, MANUF_Q, MODEL_Q, ACTIVE_IP, ACTIVE_OBJ_Q, WAN_CONN_Q, WAN_UN_Q, UPDATED_Q       
            for i in CPEModel.get_ids():
                ID = i
                serial = Processor.fetch_result(SERIAL_Q+f"c.id = {i}")
                serial = str(serial)
                serial = serial.replace('"','').replace('\'','').replace('[','').replace(']','')

                updated = Processor.fetch_result(UPDATED_Q+f"c.id = {i}")                
                updated = str(updated)
                updated = updated.replace('"','').replace('\'','').replace('[','').replace(']','')                                

                manufacturer = Processor.fetch_result(MANUF_Q+f"c.id = {i}") 
                manufacturer = str(manufacturer)
                manufacturer = manufacturer.replace('"','').replace('\'','').replace('[','').replace(']','').replace(" ","")             
                modelname = Processor.fetch_result(MODEL_Q+f"c.id = {i}")
                modelname = str(modelname)
                modelname = modelname.replace('"','').replace('\'','').replace('[','').replace(']','').replace(" ","")
                activeip = Processor.fetch_result(ACTIVE_IP+f"p.cpe_id = {i}")
                activeip = str(activeip)
                activeip = re.search('[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}',activeip)
                if activeip != None:
                    activeip = activeip.group(0)
                    activeconnection = Processor.fetch_result(ACTIVE_OBJ_Q+f"p.value = '{activeip}' and p.cpe_id = {i}")
                    activeconnection = str(activeconnection)
                    activeconnection = activeconnection.replace('"','').replace('\'','').replace('[','').replace(']','')
                    conn_param = re.sub(".WANConnectionDevice.[0-9].WANPPPConnection.[0-9].ExternalIPAddress", ".WANCommonInterfaceConfig.WANAccessType", activeconnection)
                    connectiontype = Processor.fetch_result(WAN_CONN_Q+f"n.name = '{conn_param}' and p.cpe_id = {i}")
                    connectiontype = str(connectiontype)                    
                    connectiontype = connectiontype.replace('"','').replace('\'','').replace('[','').replace(']','')
                    if connectiontype != 'DSL':
                        modulation_param = None
                        modulation_value = None
                    else:
                        modulation_param = re.sub(".WANConnectionDevice.[0-9].WANPPPConnection.[0-9].ExternalIPAddress", ".WANDSLInterfaceConfig.ModulationType", activeconnection)
                        modulation_value = Processor.fetch_result(WAN_CONN_Q+f"n.name = '{modulation_param}' and p.cpe_id = {i}")
                        modulation_value = str(modulation_value).replace('"','').replace('\'','').replace('[','').replace(']','')
                    unobj = activeconnection.replace('.ExternalIPAddress','.Username')
                    wanusername = Processor.fetch_result(WAN_UN_Q+f"n.name = '{unobj}' and p.cpe_id = {i}")
                    wanusername = str(wanusername)
                    wanusername = wanusername.replace('"','').replace('\'','').replace('[','').replace(']','')
                    json = {}                              
                    keys = ['ID','serial','manufacturer','modelname','activeip','wanusername','connectiontype', 'modulation', 'activeconnection','updated']
                    json["ID"] = ID
                    json["serial"] = serial
                    json["manufacturer"] = manufacturer
                    json["modelname"] = modelname
                    json["activeip"] = activeip
                    json["wanusername"] = wanusername
                    json["connectiontype"] = connectiontype
                    json["modulation"] = modulation_value           
                    json["activeconnection"] = activeconnection
                    json["updated"] = updated           
                    process_data = Process(target=SQLLiteProcessor.insert_data, args=(json,))                    
                    process_data.start()
                    logging.info(f"{__class__.__name__ }[Process-{process_data.pid}][CPE-{json['ID']}")                   
                    process_data.join()                                 
        except Exception as e:
            logging.error(f'{__class__.__name__ } error {e}',exc_info=1)
        finally:            
            logging.info(f'{__class__.__name__ } Result fetch end')

    @staticmethod
    def report(report_type):   
        now = datetime.datetime.now()
        date = now.strftime("%m-%d-%H-%M-%S")
        report = f'reports/CPE_Report-{report_type}-{date}.csv'         
        if report_type == 'full':
            logging.info(f"{__class__.__name__ }>[ProcessingReport: {report_type}]")
            from settings import LITE_FULL_Q        
            keys = ['ID','serial','manufacturer','modelname','activeip','wanusername','connectiontype', 'modulation', 'activeconnection','updated']
            data = SQLLiteProcessor.select_data(LITE_FULL_Q)            
            json = {
                'ID':'',
                'serial':'',
                'manufacturer':'',
                'modelname':'',
                'activeip':'',
                'wanusername':'',
                'connectiontype':'',
                'modulation':'',              
                'activeconnection':'',
                'updated':''
            }
            for item in data:
                for x,y in zip(item, json.keys()):
                    json[y] = x                     
                process_data = Process(target=CSVWritter.write_to_csv, args=(keys,report,json,))
                process_data.start()
                logging.info(f"{__class__.__name__ }[Process-{process_data.pid}][CPE-{json['ID']}")                 
                process_data.join()

        elif report_type == 'fiber':
            logging.info(f"{__class__.__name__ }>[ProcessingReport: {report_type}]")
            from settings import LITE_FIBER_Q
            keys = ['ID','serial','manufacturer','modelname','wanusername','connectiontype','updated']
            data = SQLLiteProcessor.select_data(LITE_FIBER_Q)            
            json = {
                'ID':'',
                'serial':'',
                'manufacturer':'',
                'modelname':'',                
                'wanusername':'',
                'connectiontype':'',
                'updated':''                
            }
            for item in data:
                for x,y in zip(item, json.keys()):
                    json[y] = x                     
                process_data = Process(target=CSVWritter.write_to_csv, args=(keys,report,json,))
                process_data.start()
                logging.info(f"{__class__.__name__ }[Process-{process_data.pid}][CPE-{json['ID']}")              
                process_data.join()

        elif report_type == 'dsl':
            logging.info(f"{__class__.__name__ }>[ProcessingReport: {report_type}]")
            from settings import LITE_DSL_Q
            keys = ['ID','serial','manufacturer','modelname','wanusername','connectiontype','modulation','updated']
            data = SQLLiteProcessor.select_data(LITE_DSL_Q)            
            json = {
                'ID':'',
                'serial':'',
                'manufacturer':'',
                'modelname':'',
                'wanusername':'',
                'connectiontype':'',
                'modulation':'',
                'updated':''                
            }
            for item in data:
                for x,y in zip(item, json.keys()):
                    json[y] = x                     
                process_data = Process(target=CSVWritter.write_to_csv, args=(keys,report,json,))
                process_data.start()
                logging.info(f"{__class__.__name__ }[Process-{process_data.pid}][CPE-{json['ID']}")              
                process_data.join()
        
        elif report_type == 'guest_acc':
            logging.info(f"{__class__.__name__ }>[ProcessingReport: {report_type}]")
            from settings import LITE_GUEST_Q
            keys = ['ID','serial','manufacturer','modelname','wanusername','updated']
            data = SQLLiteProcessor.select_data(LITE_GUEST_Q)            
            json = {
                'ID':'',
                'serial':'',
                'manufacturer':'',
                'modelname':'',                
                'wanusername':'',
                'updated':''                          
            }
            if data:
                for item in data:
                    for x,y in zip(item, json.keys()):
                        json[y] = x                     
                    process_data = Process(target=CSVWritter.write_to_csv, args=(keys,report,json,))
                    process_data.start()
                    logging.info(f"{__class__.__name__ }[Process-{process_data.pid}][CPE-{json['ID']}")                 
                    process_data.join()
        
        elif report_type == 'connection':
            logging.info(f"{__class__.__name__ }>[ProcessingReport: {report_type}]")
            from settings import LITE_CONN_Q
            keys = ['ID','serial','manufacturer','modelname','wanusername','connectiontype','updated']
            data = SQLLiteProcessor.select_data(LITE_CONN_Q)            
            json = {
                'ID':'',
                'serial':'',
                'manufacturer':'',
                'modelname':'',                
                'wanusername':'',
                'connectiontype':'',
                'updated':''           
            }
            if data:
                for item in data:
                    for x,y in zip(item, json.keys()):
                        json[y] = x                     
                    process_data = Process(target=CSVWritter.write_to_csv, args=(keys,report,json,))
                    process_data.start()
                    logging.info(f"{__class__.__name__ }[Process-{process_data.pid}][CPE-{json['ID']}")                 
                    process_data.join()

    @staticmethod
    def getcpe_by_un(filename):
        now = datetime.datetime.now()
        date = now.strftime("%m-%d-%H-%M-%S")
        report = f'reports/CPE_Report_from_list_{date}.csv'
        keys = ['ID','serial','manufacturer','modelname','wanusername']
        json = {
            'ID':'',
            'serial':'',
            'manufacturer':'',
            'modelname':'',
            'wanusername':'',
        }
        from settings import LITE_GETUN_FROM_LIST_Q
        try:
            logging.info(f'{__class__.__name__ } Start processing {filename}')
            usernames = []     
            with open(filename,'r') as f:
                linecount = 0
                for line in f.readlines():
                    un = line.strip()
                    usernames.append(un)

            for un in usernames:                
                data = SQLLiteProcessor.select_data(LITE_GETUN_FROM_LIST_Q+f"WHERE wanusername = '{un}';")                
                for item in data:
                    for x,y in zip(item, json.keys()):
                        json[y] = x                     
                    process_data = Process(target=CSVWritter.write_to_csv, args=(keys,report,json,))
                    process_data.start()
                    logging.info(f"{__class__.__name__ }[Process-{process_data.pid}][CPE-{json['ID']}")
                    process_data.join()

        except Exception as e:
            logging.error(f'{__class__.__name__ } Error while processing {filename}, {e}',exc_info=1)
        finally:
            logging.info(f'{__class__.__name__ } End processing {filename}')
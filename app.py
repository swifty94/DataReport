#
#   Logging configuration initialization
#
#   Customize config in logging.ini file only!
#
import sys
import logging.config
import logging
logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
from cpe_model import CPEModel
from settings import USAGE_BANNER
#
#   // TODO: implement dependency check + autoinstall from wheel (so it works offline) in case mysql.connector is missing 
#
#sp.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
#
#   Main application class
#
class App(object):    
    def collect(self):
        """
        No args needed for the function.
        \n Just use it as is: 
        \n ~$ python3 report.py collect
        """    
        try:
           logging.info(f"{__class__.__name__ } Started")
           CPEModel.process_device_data()
        except Exception as e:
            logging.error(f'{__class__.__name__ } error {e}',exc_info=1)        
        finally:
            logging.info(f"{__class__.__name__ } Ended ")
        
    def to_csv(self):
        """
        Catch CLI args to put into CSVWorker method write_to_csv() and create desired CSV report
        """
        pass

    
    def run(self):
        """
        Main application loop
        """
        try:
            cli_arguments = sys.argv[1]
            if cli_arguments:
                if cli_arguments == 'collect':
                    App.collect()
                elif cli_arguments == 'to_csv':
                    full = re.match("full", cli_arguments[2])
                    if full:
                        pass
            else:
                print("no arguments")
                exit(1)
        except IndexError as i:
            pass
            print("no arguments")

if __name__ == "__main__":
    try:
        cli_arg = sys.argv[1]
        if cli_arg == 'collect':
            CPEModel.process_device_data()
        elif cli_arg == 'report':
            try:
                next_arg = sys.argv[2]
                CPEModel.report(next_arg)
            except IndexError:
                print('Second argument is required!')
                print('Use: python app.py report $report_type')
                print('Available options: fiber, full, guest_acc')
        elif cli_arg == 'eat':
            try:
                next_arg = sys.argv[2]
                CPEModel.getcpe_by_un(next_arg)
            except IndexError:
                print('Second argument is required!')
                print('Use: python app.py eat $file_name')
                print('E.g: python3 app.py eat wan_usernames.txt')                
    except IndexError:
        print(USAGE_BANNER)
        exit(1)        
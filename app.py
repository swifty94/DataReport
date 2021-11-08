import sys
import logging.config
import logging
logging.config.fileConfig('logging.ini', disable_existing_loggers=False)
from cpe_model import CPEModel
from settings import USAGE_BANNER
from workers import SQLLiteProcessor
    
if __name__ == "__main__":
    try:
        cli_arg = sys.argv[1]
        if cli_arg == 'collect':
            SQLLiteProcessor.isDb()
            CPEModel.process_device_data()
            exit(0)
        elif cli_arg == 'report':
            try:
                next_arg = sys.argv[2]
                CPEModel.report(next_arg)
                exit(0)
            except IndexError:
                print('Second argument is required!')
                print('Use: python app.py report $report_type')
                print('Available options: fiber, full, guest_acc, connection, dsl')
                exit(1)
        elif cli_arg == 'eat':
            try:
                next_arg = sys.argv[2]
                CPEModel.getcpe_by_un(next_arg)
                exit(0)
            except IndexError:
                print('Second argument is required!')
                print('Use: python app.py eat $file_name')
                print('E.g: python3 app.py eat wan_usernames.txt')
                exit(1)
    except IndexError:
        print(USAGE_BANNER)
        exit(1)
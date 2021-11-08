# Application constants


#
#       Adjust your DB config here
#

MYSQL_DBCONFIG = {                
        'host':     'demo.friendly-tech.com',
        'user':     'ftacs',
        'password':  'ftacs',
        'database': 'ftacs',
}


#
#       MySQL queries base for each TR parameter
#

SERIAL_Q = f"""
SELECT c.serial
FROM cpe c, product_class p, manufacturer m
WHERE c.product_class_id = p.id AND
p.manufacturer_id = m.oui AND
p.manuf_id = m.id AND
"""

MANUF_Q = f"""
SELECT m.name
FROM cpe c, product_class p, manufacturer m
WHERE c.product_class_id = p.id AND
p.manufacturer_id = m.oui AND
p.manuf_id = m.id AND
"""

MODEL_Q = f"""
SELECT p.model
FROM cpe c, product_class p, manufacturer m
WHERE c.product_class_id = p.id AND
p.manufacturer_id = m.oui AND
p.manuf_id = m.id AND
"""

ACTIVE_IP = """
select p.value
from  cpe_parameter p, cpe_parameter_name n
where p.name_id=n.id and
( n.name like 'Device.ManagementServer.UDPConnectionRequestAddress' OR
n.name like 'Device.ManagementServer.ConnectionRequestURL' OR
n.name like 'Device.IP.Interface.%.IPv%Address.%.IPAddress' OR
n.name like '%.ManagementServer.ConnectionRequestURL') and
"""

ACTIVE_OBJ_Q = """
select n.name
from cpe_parameter p, cpe_parameter_name n
where p.name_id=n.id and
n.name like '%.WANPPPConnection.%.ExternalIPAddress' and        
"""

WAN_CONN_Q = """
select p.value
from cpe_parameter p, cpe_parameter_name n
where p.name_id=n.id and
"""

WAN_UN_Q = """
select p.value
from cpe_parameter p, cpe_parameter_name n
where p.name_id=n.id and
"""

UPDATED_Q = """
SELECT DATE_FORMAT(c.updated, '%Y-%m-%d_%H:%i:%S')
FROM cpe c, product_class p, manufacturer m
WHERE c.product_class_id = p.id AND
p.manufacturer_id = m.oui AND
p.manuf_id = m.id AND
"""

#
#       SQLite part
#

LITE_FULL_Q = """
SELECT cpe_id, serial, manufacturer, modelname, activeip, wanusername, connectiontype, modulation, activeconnection, updated
FROM cpeModel
ORDER BY ID ASC
"""

LITE_GUEST_Q = """
select cpe_id, serial, manufacturer, modelname, wanusername, connectiontype, updated
from cpeModel
where wanusername like '%guest%';
"""

LITE_FIBER_Q = """
select cpe_id, serial, manufacturer, modelname, wanusername, connectiontype, updated
from cpeModel
where connectiontype = 'Ethernet';
"""

LITE_DSL_Q = """
select cpe_id, serial, manufacturer, modelname, wanusername, connectiontype, modulation, updated
from cpeModel
where connectiontype = 'DSL';
"""

LITE_GETUN_FROM_LIST_Q = """
SELECT cpe_id, serial, manufacturer, modelname, wanusername, updated
FROM cpeModel
"""

LITE_CONN_Q = """
select cpe_id, serial, manufacturer, modelname, wanusername, connectiontype, updated
FROM cpeModel
"""

USAGE_BANNER = """
NO arguments provided! \n 
1. To process CPE data from FT DB and save to internall app DB use: \n
user@host:~$ python3 app.py collect \n
2. If data is processed already, you can process reports. Use: \n
user@host:~$ python3 app.py report fiber \n
Available options: full, fiber, guest_acc, connection, dsl \n
3. Obtain list of CPEs based on WAN username list. Use: \n
user@host:~$ python3 app.py eat $your_file_name E.g: \n
user@host:~$ python3 app.py eat wan_usernames.txt
"""
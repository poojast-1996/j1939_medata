import sys
import ctypes
import time
from ctypes import *
# from urllib.request import urlopen
import os

so_file = "/usr/lib/libOBD2.so"
j1939_so_file = "/usr/lib/libj1939.so"
xml_so_file = "/usr/lib/libxml2.so"
libxml2 = ctypes.CDLL(xml_so_file,mode=ctypes.RTLD_GLOBAL)
librt = ctypes.CDLL("/lib/librt-2.30.so", mode=ctypes.RTLD_GLOBAL)
j1939_func = ctypes.CDLL(j1939_so_file)

print("Init CAN")
rc = j1939_func.j1939_can_init()
print("Init CAN status", rc)
CharArr100 = (ctypes.c_char * 100)
#Structure JData
class j1939_data(Structure):
     _fields_ = [('description', CharArr100),
                ('unit', CharArr100),
                ('value', ctypes.c_double),
                ('state', CharArr100),
                ('pgn',ctypes.c_ulong),
                ('spn',ctypes.c_int32),
                ('spn_id',ctypes.c_ulong),
                ('vin', CharArr100)]
                
class DTC(Structure):
     _fields_ = [('mil_status', ctypes.c_int ),
                ('rsl_status', ctypes.c_int),
                ('awl_status', ctypes.c_int),
                ('pl_status', ctypes.c_int),
                ('spn',ctypes.c_ulong),
                ('fmi', ctypes.c_int),]
                
ar_j1939_resp = (ctypes.c_ubyte * 256)()  # 32 Bytes array
length = ctypes.c_long()
pgn = ctypes.c_ulong()  # Parameter Group Number
pointer_type = ctypes.POINTER(ctypes.c_ubyte)
spn_count=ctypes.c_long();
j_data_ptr = POINTER(j1939_data)
dtc_ptr = DTC()
j1939_func.j1939_decode_data.restype = POINTER(j1939_data)
#Loop through all the CAN messages
while True:
    rc = j1939_func.j1939_recv_broadcast_response(
    ar_j1939_resp, ctypes.byref(length), ctypes.byref(pgn))
    print("j1939_resp_recv status", rc)
    if pgn.value==61444 :
        j1939_func.get_spn_no(pgn.value, ctypes.byref(spn_count));
        print('SPN Count',spn_count.value); 
        j_data_ptr = j1939_func.j1939_decode_data(ar_j1939_resp,length,pgn,spn_count)
        print ('success')
        for i in range(spn_count.value):
            print( 'PGN',j_data_ptr[i].pgn)
            print( 'SPN',j_data_ptr[i].spn_id)
            print( 'Description',j_data_ptr[i].description)
            print( 'Value',j_data_ptr[i].value)
            print( 'Unit',j_data_ptr[i].unit)
        if pgn.value==65260:
            print ( 'VIN',j_data_ptr[0].vin);
    elif pgn.value==65226:
        j1939_func.decode_dtc(pgn,ar_j1939_resp,length,ctypes.byref(dtc_ptr))
        print ('pl_status',dtc_ptr.pl_status);
        print ('awl_status',dtc_ptr.awl_status);
        print ('mil_status',dtc_ptr.mil_status);
        print ('rsl_status',dtc_ptr.rsl_status);
        print ('SPN',dtc_ptr.spn);
        print ('FMI',dtc_ptr.fmi);
    time.sleep(1)
rc = j1939_func.j1939_can_deinit()

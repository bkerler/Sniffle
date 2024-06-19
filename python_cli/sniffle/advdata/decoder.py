# Written by Sultan Qasim Khan
# Copyright (c) 2024, NCC Group plc
# Released as open source under GPLv3

# decode.py

from struct import unpack
from .ad_types import *
from .msd_apple import AppleMSDRecord
from .msd_microsoft import MicrosoftMSDRecord
from .msd_remoteid import parse_advertising_data

# Dictionary mapping company identifiers to corresponding MSD record classes
company_msd_decoders = {
    0x0006: MicrosoftMSDRecord,
    0x004C: AppleMSDRecord
}

# Function to decode manufacturer specific data
def decode_msd(data_type: int, data: bytes):
    company, = unpack("<H", data[:2])
    if company in company_msd_decoders:
        return company_msd_decoders[company](data_type, data)
    else:
        return ManufacturerSpecificDataRecord(data_type, data)

# Dictionary mapping advertising data types to their respective classes or decoding functions
ad_type_classes = {
    0x01: FlagsRecord,
    0x02: ServiceList16Record,
    0x03: ServiceList16Record,
    0x04: ServiceList32Record,
    0x05: ServiceList32Record,
    0x06: ServiceList128Record,
    0x07: ServiceList128Record,
    0x08: ShortenedLocalNameRecord,
    0x09: CompleteLocalNameRecord,
    0x0A: TXPowerLevelRecord,
    0x16: ServiceData16Record,
    0x20: ServiceData32Record,
    0x21: ServiceData128Record,
    0xFF: parse_advertising_data  # Mapping 0xFF to the Remote ID decoding function
}

# Function to decode remote ID data
def parse_advertising_data(data):
    # Check if it's Remote ID data (0xFF service data)
    if data[0] == 0xFF:
        return decode_remote_id(data)
    else:
        return None  # Return None if not Remote ID data

def decode_adv_data(data):
    records = []
    i = 0

    while i < len(data):
        try:
            l = data[i]
            t = data[i+1]
            d = data[i+2:i+1+l]
            records.append(record_from_type_data(t, d))
            i += 1+l
        except:
            break

    return records

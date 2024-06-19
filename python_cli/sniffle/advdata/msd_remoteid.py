# msd_remoteid.py

def decode_basic_id(data):
    print("decode_basic_id function called")
    id_type = data[0] >> 4
    ua_type = data[0] & 0x0F
    drone_id = data[1:].decode('utf-8')  # Assuming drone ID is ASCII string
    return {
        'type': 'Basic ID',
        'id_type': id_type,
        'ua_type': ua_type,
        'drone_id': drone_id.strip('\x00')  # Remove null characters if any
    }

def decode_location_vector(data):
    operational_status = data[0] >> 4
    east_west_direction = (data[0] >> 1) & 0x01
    speed_multiplier = data[0] & 0x01
    direction = data[1]
    speed = data[2]
    vert_speed = data[3]
    ua_latitude = int.from_bytes(data[4:8], byteorder='big', signed=True) / 10**7  # Adjust as per actual precision
    ua_longitude = int.from_bytes(data[8:12], byteorder='big', signed=True) / 10**7  # Adjust as per actual precision
    ua_pressure_altitude = int.from_bytes(data[12:14], byteorder='big', signed=True)
    ua_geodetic_altitude = int.from_bytes(data[14:16], byteorder='big', signed=True)
    ua_height_agl = int.from_bytes(data[16:18], byteorder='big', signed=True)
    horizontal_accuracy = (data[18] >> 4) & 0x0F
    vertical_accuracy = data[18] & 0x0F
    baro_accuracy = data[19] >> 4
    speed_accuracy = data[19] & 0x0F
    timestamp = int.from_bytes(data[20:23], byteorder='big') / 10  # Timestamp in 1/10 seconds
    timestamp_accuracy = data[23]
    return {
        'type': 'Location/Vector',
        'operational_status': operational_status,
        'east_west_direction': 'West' if east_west_direction else 'East',
        'speed_multiplier': speed_multiplier,
        'direction': direction,
        'speed': speed,
        'vert_speed': vert_speed,
        'ua_latitude': ua_latitude,
        'ua_longitude': ua_longitude,
        'ua_pressure_altitude': ua_pressure_altitude,
        'ua_geodetic_altitude': ua_geodetic_altitude,
        'ua_height_agl': ua_height_agl,
        'horizontal_accuracy': horizontal_accuracy,
        'vertical_accuracy': vertical_accuracy,
        'baro_accuracy': baro_accuracy,
        'speed_accuracy': speed_accuracy,
        'timestamp': timestamp,
        'timestamp_accuracy': timestamp_accuracy
    }

def decode_self_id(data):
    description_type = data[0] >> 4
    description = data[1:].decode('utf-8')  # Assuming description is ASCII string
    return {
        'type': 'Self-ID',
        'description_type': description_type,
        'description': description.strip('\x00')  # Remove null characters if any
    }

def decode_system(data):
    classification_type = data[0] >> 6
    operator_location_type = (data[0] >> 4) & 0x03
    operator_latitude = int.from_bytes(data[1:5], byteorder='big', signed=True) / 10**7  # Adjust as per actual precision
    operator_longitude = int.from_bytes(data[5:9], byteorder='big', signed=True) / 10**7  # Adjust as per actual precision
    area_count = data[9]
    area_radius = int.from_bytes(data[10:12], byteorder='big')
    area_ceiling = int.from_bytes(data[12:14], byteorder='big')
    area_floor = int.from_bytes(data[14:16], byteorder='big')
    ua_classification_category = (data[16] >> 4) & 0x0F
    operator_geodetic_alt = int.from_bytes(data[16:18], byteorder='big', signed=True)
    message_timestamp = int.from_bytes(data[18:22], byteorder='big')
    return {
        'type': 'System',
        'classification_type': classification_type,
        'operator_location_type': operator_location_type,
        'operator_latitude': operator_latitude,
        'operator_longitude': operator_longitude,
        'area_count': area_count,
        'area_radius': area_radius,
        'area_ceiling': area_ceiling,
        'area_floor': area_floor,
        'ua_classification_category': ua_classification_category,
        'operator_geodetic_alt': operator_geodetic_alt,
        'message_timestamp': message_timestamp
    }

def decode_operator_id(data):
    operator_id_type = data[0] >> 4
    operator_id = data[1:].decode('utf-8')  # Assuming operator ID is ASCII string
    return {
        'type': 'Operator ID',
        'operator_id_type': operator_id_type,
        'operator_id': operator_id.strip('\x00')  # Remove null characters if any
    }

def decode_remote_id(data):
    message_type = data[0] >> 4
    if message_type == 0:
        return decode_basic_id(data)
    elif message_type == 1:
        return decode_location_vector(data)
    elif message_type == 3:
        return decode_self_id(data)
    elif message_type == 4:
        return decode_system(data)
    elif message_type == 5:
        return decode_operator_id(data)
    else:
        return {'type': 'Unknown'}

def parse_advertising_data(advertising_data):
    # Extract Service Data - 16 bit UUID details
    if advertising_data[0] == 0x16:
        uuid16 = (advertising_data[2] << 8) | advertising_data[1]
        if uuid16 == 0xFFFA:  # Check for ASTM Remote ID
            service_data_length = advertising_data[3]
            service_data = advertising_data[4:4 + service_data_length]
            return decode_remote_id(service_data)

    return None  # Return None if the data doesn't match expected format

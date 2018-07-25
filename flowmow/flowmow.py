import numpy as np
import scipy.io as sio
import datetime as dt
import io
import requests
import pandas as pd

def _get_timestamp(line):
    """ Get a datetime and epoch value from a standard DAT file line """
    timestamp = dt.datetime.strptime(' '.join(line.strip().split(' ')[1:3]), '%Y/%m/%d %H:%M:%S.%f')
    epoch = np.float64(timestamp.replace(tzinfo=dt.timezone.utc).timestamp()) # 'epoch' is unix time
    return timestamp, epoch

def _get_token(response):
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            return value
    return None

def open_gdrive_file(blob_id):
    """ Read a file from Google Drive into memory. Returns an open (BytesIO) file-like object. """
    
    url = "https://docs.google.com/uc?export=download"
    session = requests.Session()
    response = session.get(url, params = { 'id' : blob_id }, stream = True,)
    token = _get_token(response)
    if token:
        params = { 'id' : blob_id, 'confirm' : token }
        response = session.get(url, params = params, stream = True)
    file_bytes = response.content
    return io.BytesIO(file_bytes)

def read_nav(blob_id, dive_number):
    f = open_gdrive_file(blob_id)
    mat = sio.loadmat(f, squeeze_me=True)
    nrows = len(mat['rnv']['t'].take(0))
    timestamp = []
    for i in range(nrows):
        timestamp.append(dt.datetime.utcfromtimestamp(mat['rnv']['t'].take(0)[i]))
    epoch = list(mat['rnv']['t'].take(0))        
    dive_number = [dive_number] * nrows
    lat = list(mat['rnv']['lat'].take(0))
    lon = list(mat['rnv']['lon'].take(0))
    depth = list(mat['rnv']['pos'].take(0)[:,2])
    height = list(mat['rnv']['alt'].take(0))
    heading = list(mat['rnv']['pos'].take(0)[:,3])
    pitch = list(mat['rnv']['pos'].take(0)[:,4])
    roll = list(mat['rnv']['pos'].take(0)[:,5])
    
    # convert to dataframe
    return pd.DataFrame({'timestamp': timestamp, 'epoch': epoch, 'dive_number': dive_number,
                        'lat': lat, 'lon': lon, 'depth': depth, 'heading': heading,
                        'pitch': pitch, 'roll': roll, 'height': height})

def read_paros(blob_id, dive_number):
    paros_list = []
    f = open_gdrive_file(blob_id)
    for line in f:
        line = line.decode('utf-8').strip()
        if 'RAW' in line[0:3]:
            if 'P2=' in line:
                if len(line) == 57: # good lines from this instrument are length 57
                    timestamp, epoch = _get_timestamp(line)
                    a = line.split(' ')[3].split(',')[0].split('=')[1]
                    b = line.split(' ')[3].split(',')[1]
                    paros_list.append([timestamp, epoch, dive_number, np.float64(a), np.float64(b)])

    # convert to dataframe (tau and eta are the the pressure and temperature signal periods in microseconds)
    return pd.DataFrame(paros_list, columns=['timestamp', 'epoch', 'dive_number', 'tau', 'eta'])

def read_ustrain(blob_id, dive_number):
    ustrain_list = []
    f = open_gdrive_file(blob_id)
    for line in f:
        line = line.decode('utf-8').strip()
        if 'MSA3' in line[0:4]:
            if len(line.split(' ')) == 32: # good lines from this instrument will have 32 fields
                timestamp, epoch = _get_timestamp(line)
                ustrain_list.append([timestamp, epoch, dive_number] + list(map(np.float64, line.split(' ')[3:-1])))

    # convert to dataframe
    return pd.DataFrame(ustrain_list, columns=['timestamp','epoch','dive_number','a',
                                              'b','c','d','e','f','g','h','i','j','k',
                                              'l','m','n','o','p','q','r','s','t','u',
                                              'v','w','x','y','z','aa','bb'])

def read_sbe3(blob_id, dive_number):
    sbe3_list = []
    f = open_gdrive_file(blob_id)
    for line in f:
        try:
            line = line.decode('utf-8').strip()
        except:
            line = ''
        if 'SBE3' in line[0:4]:
            if len(line) == 58: # good lines from this instrument are length 58
                timestamp, epoch = _get_timestamp(line)
                counts_0 = np.int64(line.split(' ')[4])
                counts_1 = np.int64(line.split(' ')[6])
                if counts_0 > 500000 and counts_0 < 815000 and counts_1 > 450000 and counts_1 < 770000:
                    sbe3_list.append([timestamp, epoch, dive_number, counts_0, counts_1])

    # convert to dataframe
    return pd.DataFrame(sbe3_list, columns=['timestamp','epoch','dive_number','counts_0','counts_1'])

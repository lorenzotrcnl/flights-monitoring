import time 
import json 
import random 
from datetime import datetime
from kafka import KafkaProducer
from FlightRadar24.api import FlightRadar24API


# Messages will be serialized as JSON 
def serializer(message):
    return json.dumps(message).encode('utf-8')


# Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=['kafka1:9092','kafka2:9092'],
    value_serializer=serializer
)

def get_boundaries():
    # Get boundaries for each zone
    boundsALL = {}

    zones = 'germany,uk,spain,france,italy'
    for zone in zones.split(','):
        boundsALL[zone] = frApi.get_bounds(frApi.get_zones()['europe']['subzones'][zone])

    return boundsALL
        


if __name__ == '__main__':
    print("[INITIALIZING]")
    frApi = FlightRadar24API()
    boundaries = get_boundaries()
    
    print("[READY]")
    
    itr = 1
    # Infinite loop - runs until you kill the program
    while True:
        
        print("[STARTING STREAM]")
        print("#",itr)
        st = datetime.now()
        
        flights = []
        for bound in boundaries.items(): # for each zone
            for fli in frApi.get_flights(bounds = bound[1]): # get flights
                dat = vars(fli)
                dat['ts'] = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')
                dat['at_zone'] = bound[0]
                flights.append(dat)
            
        random.shuffle(flights) # simulating data ingestion randomness

        for i, fli in enumerate(flights):
            if (i%100)==0:
                print('SENDING MESSAGES ------------------> ', fli["at_zone"], ' | ', datetime.now(), ' CURRENT: ', i, '/', len(flights))
            producer.send('apicall', fli)
            time.sleep(random.uniform(0.004, 0.06))
            
        et = datetime.now()
        print("Stream execution time -------------------> ", et - st, " seconds")
        itr+=1
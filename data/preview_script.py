
import time
import random
import datetime
import signal
import sys
import csv
import uuid
from datetime import datetime, timedelta

# Costanti e configurazione
CARRIERS = ["Tata Communications", "Verizon", "BT Wholesale", "Telia Carrier", "Orange International Carriers", "Deutsche Telekom ICSS"]
COUNTRIES = ["IT:Italy", "FR:France", "DE:Germany", "US:United States", "GB:United Kingdom", "ES:Spain"]
SELLING_DEST = ["IT_Mobile", "FR_Mobile", "DE_Mobile", "US_Mobile", "GB_Mobile", "ES_Mobile"]

def generate_records(num_records):
    records = []
    for i in range(num_records):
        val_euro = round(random.uniform(0.1, 10.0), 2)
        duration = random.randint(1, 3600)
        country_code, country_name = random.choice(COUNTRIES).split(":")
        carrier_in = random.choice(CARRIERS)
        carrier_out = random.choice(CARRIERS)
        selling_dest = random.choice(SELLING_DEST)

        raw_caller_number = ''.join(random.choices('0123456789', k=12))
        raw_called_number = ''.join(random.choices('0123456789', k=12))

        timestamp = datetime.now().isoformat()[:-3] + "Z"
        timestamp = datetime.now().astimezone().isoformat()

        record = {
            "tenant": "Sparkle",
            "val_euro": val_euro,
            "duration": duration,
            "economicUnitValue": val_euro,
            "other_party_country": country_code,
            "routing_dest": selling_dest,
            "service_type__desc": "Voice",
            "op35": None,
            "carrier_in": carrier_in,
            "carrier_out": carrier_out,
            "selling_dest": selling_dest,
            "raw_caller_number": raw_caller_number,
            "raw_called_number": raw_called_number,
            "paese_destinazione": country_name,
            "timestamp": timestamp,
            "xdrid": str(uuid.uuid4())
        }
        records.append(record)
    return records

def save_to_csv(records, filename):
    fields = ["tenant", "val_euro", "duration", "economicUnitValue", "other_party_country",
              "routing_dest", "service_type__desc", "op35", "carrier_in", "carrier_out",
              "selling_dest", "raw_caller_number", "raw_called_number", "paese_destinazione",
              "timestamp", "xdrid"]
    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)
    print(f"File generato: {filename}")

def main():
    try:
        print(f"Inizio generazione: {datetime.now()}")

        # Generazione record
        records = generate_records(num_records=100)

        # Nome file basato su timestamp
        now = datetime.now()
        filename = f"output_{now.strftime('%Y%m%d%H%M%S')}.csv"

        # Salvataggio
        save_to_csv(records, filename)


    except KeyboardInterrupt:
        print("\nGenerazione interrotta dall'utente")
        sys.exit(0)

if __name__ == "__main__":
    main()

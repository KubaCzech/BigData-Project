import time
import random
from datetime import datetime, timedelta
from cassandra.cluster import Cluster, ExecutionProfile, EXEC_PROFILE_DEFAULT
from cassandra.query import BatchStatement, SimpleStatement, PreparedStatement
from cassandra.policies import RoundRobinPolicy, RetryPolicy
from cassandra import ConsistencyLevel
from uuid import uuid4

# For simplicity all reservations can be make one week ahaed, e. g. 16 June to 22 June 
class ReservationSystem:
    def __init__(self, nr_of_clients, nr_of_tables, nr_of_res):
        self.nr_of_clients = nr_of_clients
        self.nr_of_tables = nr_of_tables
        self.nr_of_res = nr_of_res

        my_profile = ExecutionProfile(
            consistency_level=ConsistencyLevel.QUORUM,
            load_balancing_policy=RoundRobinPolicy(),
            request_timeout=10
        )

        # cluster = Cluster(['127.0.0.1', '127.0.0.2', '127.0.0.3'], port=9043, execution_profiles=my_profile)
        cluster = Cluster(['127.0.0.1'], port=9043, execution_profiles={EXEC_PROFILE_DEFAULT: my_profile})
        self.session = cluster.connect('reservations')
        print("Succesfully connected to cluster")

        # If there are any existing tables, delete them so we can start fresh
        self.session.execute("DROP TABLE IF EXISTS reservations.reservations;")
        self.session.execute("DROP TABLE IF EXISTS reservations.customers;")
        self.session.execute("DROP TABLE IF EXISTS reservations.tables;")
        time.sleep(1)

        # Create appropriate tables: reservations, tables, customers
        query = 'CREATE TABLE IF NOT EXISTS reservations (res_ID uuid, client_ID uuid, beg_of_res timestamp, end_of_res timestamp, number_of_guests int, table_id uuid, PRIMARY KEY (res_ID));'
        self.session.execute(query)

        query = 'CREATE TABLE IF NOT EXISTS tables (table_ID uuid, nr_of_seats int, PRIMARY KEY (table_ID));'
        self.session.execute(query)

        query = 'CREATE TABLE IF NOT EXISTS customers (customer_ID uuid, name text, surname text, PRIMARY KEY (customer_ID));'
        self.session.execute(query)
        time.sleep(1)

        # Generate initial data - tables, customers and reservations
        self.make_initial_clients()
        print("Succesfully filled table tables")
        time.sleep(1)

        self.make_initial_tables()
        print("Succesfully filled table customers")
        time.sleep(1)

        self.make_initial_reservations()
        print("Succesfully filled table reservations")

    # Function to generate clients
    # DONE
    def make_initial_clients(self):
        insert_client = self.session.prepare("INSERT INTO customers (customer_ID, name, surname) VALUES (?, ?, ?)")

        names = ['Alice', 'Bob', 'Charlie', 'David', 'Eva', 'Frank', 'Grace', 'Helen', 'Ian', 'Jane']
        surnames = ['Smith', 'Johnson', 'Brown', 'Williams', 'Jones', 'Garcia', 'Miller', 'Davis', 'Martinez', 'Wilson']

        batch = BatchStatement()
        for i in range(self.nr_of_clients):
            customer_id = uuid4()
            # customer_id = i
            name = names[random.randint(0, len(names)-1)]
            surname = surnames[random.randint(0, len(surnames)-1)]
            batch.add(insert_client, (customer_id, name, surname))
        
        self.session.execute(batch)

    # Function to generate tables
    # DONE
    def make_initial_tables(self):
        insert_table = self.session.prepare("INSERT INTO tables (table_ID, nr_of_seats) VALUES (?, ?)")

        batch = BatchStatement()

        for i in range(self.nr_of_tables):
            table_id = uuid4()
            # table_id = i
            nr_of_seats = random.randint(2, 12)
            batch.add(insert_table, (table_id, nr_of_seats))

        self.session.execute(batch)

    # Function to generate random data for initial reservations
    # DONE
    def generate_reservation_data(self):
        customers_ids = [row.customer_id for row in self.session.execute("SELECT customer_id FROM customers;")]

        client_ID = random.choice(customers_ids)

        beg_of_res = datetime(year=2025, month=6, day = random.randint(16, 16), 
                              hour = random.randint(12, 22), minute=random.choice(range(0, 60, 15)))
        for_how_long = random.choice(range(30, 135, 15)) # Between half and two hours
        end_of_res = beg_of_res + timedelta(minutes=for_how_long)

        number_of_guests = random.randint(1, 10)
        return (client_ID, beg_of_res, end_of_res, number_of_guests)
    
    # Check if data generated this time is consistent with previous data and assign table id;
    # If None is returned, reservation cannot be made
    # DONE
    def assign_table_number(self, new_data, records, free = False):
        beg_of_res_new = new_data[1]
        end_of_res_new = new_data[2]
        nr_of_guests_new = new_data[3]

        table_rows = self.session.execute("SELECT table_id, nr_of_seats FROM tables")
        all_tables = [
            (row.table_id, row.nr_of_seats) for row in table_rows if row.nr_of_seats >= nr_of_guests_new
        ]

        occupied_tables = set()
        for rec in records:
            table_id = rec[5]
            beg_of_res = rec[2]
            end_of_res = rec[3]
            if not (end_of_res <= beg_of_res_new or beg_of_res >= end_of_res_new):
                occupied_tables.add(table_id)

        available_tables = [i for i in all_tables if i[0] not in occupied_tables]
        if len(available_tables) < 1:
            return None
        available_tables.sort(key = lambda x: x[1])
        if free:
            return [available_tables[i][0] for i in range(len(available_tables))]
        else:
            return available_tables[0][0]

    # Function to generate reservations
    # DONE
    def make_initial_reservations(self):
        insert_res = self.session.prepare(
            "INSERT INTO reservations (res_id, client_id, beg_of_res, end_of_res, number_of_guests, table_id) VALUES (?, ?, ?, ?, ?, ?)"
            )
        batch = BatchStatement()
        records = []
        while len(records) < self.nr_of_res:
            res_id = uuid4()
            client_ID, beg_of_res, end_of_res, number_of_guests = self.generate_reservation_data()
            table_id = self.assign_table_number([client_ID, beg_of_res, end_of_res, number_of_guests], records)
            if table_id is None:
                continue
            else:
                batch.add(insert_res, (res_id, client_ID, beg_of_res, end_of_res, number_of_guests, table_id))
                records.append([res_id, client_ID, beg_of_res, end_of_res, number_of_guests, table_id])
            if len(batch) >= 15:
                self.session.execute(batch)
                batch = BatchStatement()
        self.session.execute(batch)
    
    # Function to make a reservation, given appropriate information
    # DONE
    def make_reservation(self, client_id, beg_of_res, end_of_res, number_of_guests, table_ = None):
        query = 'SELECT res_ID, client_ID, beg_of_res, end_of_res, number_of_guests, table_id FROM reservations'
        records = list(self.session.execute(query))
        new_data = [client_id, beg_of_res, end_of_res, number_of_guests]

        if table_ is None:
            table_id = self.assign_table_number(new_data, records)
        else:
            # Check if table is ok
            free_tables = self.assign_table_number(new_data, records, free = True)          
            if table_ in free_tables:
                table_id = table_
            else:
                # print('Cant assign table, already occupied')
                return

        if table_id is None:
            # print("No available table for given time and guest count.")
            return None
        else:
            insert_res = self.session.prepare(
                "INSERT INTO reservations (res_id, client_id, beg_of_res, end_of_res, number_of_guests, table_id) VALUES (?, ?, ?, ?, ?, ?)"
            )
            res_id = uuid4()
            self.session.execute(insert_res, (res_id, client_id, beg_of_res, end_of_res, number_of_guests, table_id))
            # print(f"Reservation made with id {res_id} at table {table_id}")
        return res_id

    # Function to update a reservation based on what we want to update
    # DONE
    def update_reservation(self, id_of_res, client_id=None, beg_of_res=None, end_of_res=None, number_of_guests=None):
        old_info = list(self.session.execute(
        "SELECT * FROM reservations WHERE res_id = %s", [id_of_res]
        ))
        if not old_info:
            print("Reservation not found.")
            return

        old_info = old_info[0]
        client_id = client_id if client_id is not None else old_info.client_id
        beg_of_res = beg_of_res if beg_of_res is not None else old_info.beg_of_res
        end_of_res = end_of_res if end_of_res is not None else old_info.end_of_res
        number_of_guests = number_of_guests if number_of_guests is not None else old_info.number_of_guests

        # Fetch all current reservations for overlap checking
        all_records = list(self.session.execute("SELECT * FROM reservations"))
        all_records = [r for r in all_records if r.res_id != id_of_res]

        # Try to reassign a table if time or guest count changed
        if (beg_of_res != old_info.beg_of_res or 
            end_of_res != old_info.end_of_res or 
            number_of_guests != old_info.number_of_guests):
            new_data = [client_id, beg_of_res, end_of_res, number_of_guests]
            table_id = self.assign_table_number(new_data, all_records)
            if table_id is None:
                # print("No table available for updated time or guest count.")
                return
        else:
            table_id = old_info.table_id

        # Perform the update
        update_query = self.session.prepare("""
            UPDATE reservations
            SET client_id = ?, beg_of_res = ?, end_of_res = ?, number_of_guests = ?, table_id = ?
            WHERE res_id = ?
        """)
        self.session.execute(update_query, (client_id, beg_of_res, end_of_res, number_of_guests, table_id, id_of_res))
        print(f"Reservation {id_of_res} updated.")

    # DONE
    def see_reservation(self, id_of_res):
        res = self.session.execute(f"SELECT * FROM reservations where res_id = {id_of_res}")[0]
        client_id = res.client_id
        client = [i for i in self.session.execute(f"SELECT * FROM customers where customer_id = {client_id}")][0]
        print(f"Reservation id: {res.res_id},\nStart of res: {res.beg_of_res},\nEnd of res: {res.end_of_res},\nClient Name: {client.name},\nClient surname: {client.surname},\nTable id: {res.table_id}\n\n")
        return res

    # DONE
    def see_all_reservations(self):
        rows = self.session.execute("SELECT * FROM reservations")
        for row in rows:
            print(row)
        return rows
    
    def shutdown(self):
        self.session.shutdown()
        self.session.cluster.shutdown()


if __name__ == '__main__':
    system = ReservationSystem(20, 10, 100)
    tables = system.session.execute("SELECT * FROM tables")
    customers = system.session.execute("SELECT * FROM customers")
    reservations = system.session.execute("SELECT * FROM reservations")
    reservations = sorted(reservations, key = lambda x: (x.table_id, x.beg_of_res))

    for t in tables:
        print(t)

    for c in customers:
        print(c)

    # See reservations
    for r in reservations:
        print(r)

    # Make reservation
    customers_ids = [row.customer_id for row in system.session.execute("SELECT customer_id FROM customers;")]
    client_ID = random.choice(customers_ids)

    beg_of_res = datetime(year=2025, month=6, day = 17, 
                              hour = random.randint(12, 22), minute=random.choice(range(0, 60, 15)))
    for_how_long = random.choice(range(30, 135, 15)) # Between half and two hours
    end_of_res = beg_of_res + timedelta(minutes=for_how_long)

    nr_of_guests = 2

    system.make_reservation(client_ID, beg_of_res, end_of_res, nr_of_guests)

    # Update reservation
    res_ids = [row.res_id for row in system.session.execute("SELECT res_id FROM reservations;")]
    res_id = random.choice(res_ids)

    client_ID = 123

    system.see_reservation(res_id)

    client_id = random.choice(customers_ids)
    system.update_reservation(res_id, client_id=client_id)
    system.see_reservation(res_id)

    system.shutdown()
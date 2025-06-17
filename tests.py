import random
import unittest
import threading
import time
from datetime import datetime, timedelta
from project import ReservationSystem

class ReservationSystemTester(unittest.TestCase):
    def __init__(self, reservation_system: ReservationSystem):
        self.system = reservation_system
        self.client_ids = self._get_client_ids()
        self.table_ids = self._get_table_ids()

    def _get_client_ids(self):
        customers = self.system.session.execute("SELECT customer_id FROM customers")
        return [row.customer_id for row in customers]
    
    def _get_table_ids(self):
        tables = self.system.session.execute("SELECT table_id FROM tables")
        return [row.table_id for row in tables]

    def stress_test_1(self):
        print("Running Stress Test 1 (Rapid same request from one client)...")
        client_id = self.client_ids[0]
        table_id = self.table_ids[0]

        def spam_reservations():
            for _ in range(10):
                start = datetime(2025, 6, 17, hour=12, minute=0)
                end = start + timedelta(minutes=60)
                self.system.make_reservation(client_id, start, end, 2, table_=table_id)
                time.sleep(0.1)

        t = threading.Thread(target=spam_reservations)
        t.start()
        t.join()
        print("Stress Test 1 complete.\n")

    def stress_test_2(self, num_threads=5):
        print("Running Stress Test 2 (Multiple clients making random requests)...")

        def random_reservation(client_id):
            for _ in range(5):
                start = datetime(2025, 6, 16, hour=random.randint(12, 22), minute=random.choice(range(0, 60, 15)))
                end = start + timedelta(minutes=random.choice([15, 30, 45, 60]))
                guests = random.randint(1, 10)

                self.system.make_reservation(client_id, start, end, guests)
                time.sleep(random.uniform(0.1, 0.3))

        threads = []
        for _ in range(num_threads):
            cid = random.choice(self.client_ids)
            t = threading.Thread(target=random_reservation, args=(cid,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()
        print("Stress Test 2 complete.\n")

    def stress_test_3(self):
        print("Running Stress Test 3 (Two clients try to fully occupy the system)...")

        def fill_up(client_id):
            for _ in range(75):  # Attempt 75 reservations per client
                start = datetime(2025, 6, 18, hour=random.randint(12, 22), minute=random.choice(range(0, 60, 15)))
                end = start + timedelta(minutes=90)
                guests = random.randint(1, 4)
                self.system.make_reservation(client_id, start, end, guests)

        t1 = threading.Thread(target=fill_up, args=(self.client_ids[0],))
        t2 = threading.Thread(target=fill_up, args=(self.client_ids[1],))
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        print("Stress Test 3 complete.\n")

    def run_all_tests(self):
        self.stress_test_1()
        self.stress_test_2()
        self.stress_test_3()

        print("All stress tests completed. Final reservations:\n")
        self.system.see_all_reservations()

if __name__ == '__main__':
    system = ReservationSystem(20, 10, 100)
    tester = ReservationSystemTester(system)
    time.sleep(1)

    # Stress test 1
    tester.stress_test_1()
    system.see_all_reservations()
    print(len([i for i in system.session.execute("SELECT * FROM reservations")]))

    # Stress test 2
    tester.stress_test_2()
    print(len([i for i in system.session.execute("SELECT * FROM reservations")]))

    # Stress test 3
    tester.stress_test_3()
    rows = [i for i in system.session.execute("SELECT * FROM reservations")]
    rows.sort(key = lambda x: (x.beg_of_res, x.client_id))
    for row in rows:
        print(row.client_id, row.beg_of_res, row.end_of_res)

    system.shutdown()
import random
import unittest
import threading
import time
from datetime import datetime, timedelta
from project import ReservationSystem

class ReservationSystemTester(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.system = ReservationSystem(20, 10, 100)
        time.sleep(1)
        cls.client_ids = cls._get_client_ids()
        cls.table_ids = cls._get_table_ids()

    @classmethod
    def _get_client_ids(self):
        customers = self.system.session.execute("SELECT customer_id FROM customers")
        return [row.customer_id for row in customers]
    
    @classmethod
    def _get_table_ids(self):
        tables = self.system.session.execute("SELECT table_id FROM tables")
        return [row.table_id for row in tables]

    def test_1(self):
        # Running Stress Test 1 (Rapid same request from one client
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

    def test_2(self, num_threads=5):
        # Running Stress Test 2 (Multiple clients making random requests
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

    def test_3(self):
        # Running Stress Test 3 (Two clients try to fully occupy the system
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

if __name__ == '__main__':
    unittest.main()
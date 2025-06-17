import uuid
from project import ReservationSystem
from datetime import datetime

def main(N1, N2, N3):
    system = ReservationSystem(N1, N2, N3)
    while True:
        message = "Choose what to do:\n" \
        "0. Exit the program\n" \
        "1. See all reservations\n" \
        "2. See all reservations for specific day\n" \
        "3. See specific reservation\n" \
        "4. See all reservations for the specific customer\n" \
        "5. See clients IDs\n" \
        "6. See tables\n" \
        "7. Make reservation\n" \
        "8. Update reservation\n"\
        "9. Delete reservation\n"
        print(message)
        choice = int(input('Choice: '))

        if choice == 0:
            print("Closing system")
            break
            
        elif choice == 1:
            res = system.get_all_reservations()
            for r in res:
                system.see_reservation(r.res_id)

        elif choice == 2:
            date = input("Provide date: ")
            rows = system.get_all_reservations_for_date(date)
            print(f"Reservations made for {date}:")
            for r in rows:
                system.see_reservation(r.res_id)
            

        elif choice == 3:
            print("Provide reservation ID\n")
            res_id = input("Reservation ID: ")
            system.see_reservation(res_id)
        
        elif choice == 4:
            id = input("Provide customer's ID: \n")
            rows = system.get_all_reservations_for_customer(id)
            print(f"Reservations for customer {id}:")
            for r in rows:
                system.see_reservation(r.res_id)
   
        elif choice == 5:
            clients = system.get_all_customers()
            cnt = 1
            for c in clients:
                print(f"{cnt}.\nID of client: {c.customer_id},\nName: {c.name}\nSurname: {c.surname}\n")
                cnt += 1
        
        elif choice == 6:
            tables = system.get_all_tables()
            cnt = 1
            for t in tables:
                print(f"{cnt}.\nID of table: {t.table_id},\nNumber of seats: {t.nr_of_seats}\n")
                cnt += 1
        
        elif choice == 7:
            str_f = "%Y-%m-%d %H:%M"
            print("Do you want random?\n")

            y = input("Yes/no: ")
            if y in ['No', 'no']:
                id = input("client ID: ")
                id = uuid.UUID(id)
                beg_of_res = input("Beggining of reservation: ")
                beg_of_res = datetime.strptime(beg_of_res, str_f)
                end_of_res = input("End of reservation: ")
                end_of_res = datetime.strptime(end_of_res, str_f)
                nr_of_guests = int(input("Number of guests: "))
                system.make_reservation(id, beg_of_res, end_of_res, nr_of_guests)

            else:
                c, b, e, n = system.generate_reservation_data()
                system.make_reservation(c, b, e, n)
        
        elif choice == 8:
            str_f = "%Y-%m-%d %H:%M"
            client_id, beg_of_res, end_of_res, nr_of_guests = None, None, None, None
            res_id = input("Reservation id: ")
            res_id = uuid.UUID(res_id)

            print("What do you want to update?")
            y1 = input("Client ID? [Yes/no]: ")
            if y1 in ['yes', 'Yes']:
                client_id = input("Provide new client ID: ")
                client_id = uuid.UUID(client_id)

            y2 = input("Beggining of reservation? [Yes/no]: ")
            if y2 in ['yes', 'Yes']:
                beg_of_res = input("Provide new beggining of reservation: ")
                beg_of_res = datetime.strptime(beg_of_res, str_f)

            y3 = input("End of reservation? [Yes/no]: ")
            if y3 in ['yes', 'Yes']:
                end_of_res = input("Provide new end of reservation: ")
                end_of_res = datetime.strptime(end_of_res, str_f)


            y4 = input("Number of guests? [Yes/no]: ")
            if y4 in ['yes', 'Yes']:
                nr_of_guests = int(input("Provide new number of guests"))

            system.update_reservation(res_id, client_id = client_id, beg_of_res = beg_of_res, end_of_res = end_of_res, number_of_guests = nr_of_guests)
                    
        elif choice == 9:
            id = input("Provide ID of reservation to delete: ")
            id = uuid.UUID(id)
            system.delete_reservation(id)
        
        else:
            print("Incorrect option was selected. Choose again")

if __name__ == '__main__':
    main(20, 10, 10)
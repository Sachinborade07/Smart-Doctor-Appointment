import psycopg2
from datetime import datetime, timedelta, time

def generate_doctor_slots(
    doctor_id: int = 1,
    days_to_generate: int = 5,
    slot_duration_minutes: int = 15,
    db_config: dict = {
        "dbname": "DoctorApp",
        "user": "postgres",
        "password": "root",
        "host": "localhost",
        "port": "5432"
    }
):
    conn = psycopg2.connect(**db_config)
    cur = conn.cursor()

    slot_duration = timedelta(minutes=slot_duration_minutes)
    start_morning = time(10, 0)
    end_morning = time(12, 0)
    start_afternoon = time(13, 0)
    end_afternoon = time(17, 0)

    cur.execute("""
        DELETE FROM doctor_availability_slots
        WHERE slot_date < CURRENT_DATE AND doctor_id = %s;
    """, (doctor_id,))

    for day in range(days_to_generate):
        slot_date = (datetime.today() + timedelta(days=day)).date()

        def insert_slots(start, end):
            current = datetime.combine(slot_date, start)
            end_dt = datetime.combine(slot_date, end)
            while current < end_dt:
                next_slot = current + slot_duration

                cur.execute("""
                    SELECT 1 FROM doctor_availability_slots
                    WHERE doctor_id = %s AND slot_date = %s
                      AND start_time = %s AND end_time = %s
                """, (doctor_id, slot_date, current.time(), next_slot.time()))
                exists = cur.fetchone()

                if not exists:
                    cur.execute("""
                        INSERT INTO doctor_availability_slots (doctor_id, slot_date, start_time, end_time, is_booked)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (doctor_id, slot_date, current.time(), next_slot.time(), False))

                current = next_slot

        insert_slots(start_morning, end_morning)
        insert_slots(start_afternoon, end_afternoon)

    conn.commit()
    cur.close()
    conn.close()

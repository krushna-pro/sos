import csv
import random

# You can change how many dummy students you want
N_STUDENTS = 20

departments = ["CSE", "IT", "ECE", "ME", "CIVIL"]


def generate_student_ids(n):
    return [f"S{i:03d}" for i in range(1, n + 1)]


def generate_base_csv(student_ids):
    """
    For /students/import-base-csv
    Header:
    student_id,name,email,phone,department,semester,
    attendance_percentage,cgpa,backlogs,fees_pending,fees_amount_due,
    parent_name,parent_phone,parent_email
    """
    filename = "students_base.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "student_id",
            "name",
            "email",
            "phone",
            "department",
            "semester",
            "attendance_percentage",
            "cgpa",
            "backlogs",
            "fees_pending",
            "fees_amount_due",
            "parent_name",
            "parent_phone",
            "parent_email",
        ])

        for sid in student_ids:
            idx = int(sid[1:])
            name = f"Student {idx}"
            email = f"student{idx}@example.com"
            phone = f"9000000{idx:03d}"
            dept = random.choice(departments)
            semester = random.randint(1, 8)
            attendance = round(random.uniform(40, 95), 1)
            cgpa = round(random.uniform(4.0, 9.5), 1)
            backlogs = random.choice([0, 0, 1, 2, 3])
            fees_pending = random.choice(["true", "false", "false"])
            fees_amount = 0.0 if fees_pending == "false" else random.choice([15000, 25000, 35000])
            parent_name = f"Parent {idx}"
            parent_phone = f"9888888{idx:03d}"
            parent_email = f"parent{idx}@example.com"

            w.writerow([
                sid,
                name,
                email,
                phone,
                dept,
                semester,
                attendance,
                cgpa,
                backlogs,
                fees_pending,
                fees_amount,
                parent_name,
                parent_phone,
                parent_email,
            ])

    print(f"Generated {filename}")


def generate_attendance_csv(student_ids):
    """
    For /students/import-attendance-csv
    Header:
    student_id,attendance_percentage
    """
    filename = "attendance.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["student_id", "attendance_percentage"])
        for sid in student_ids:
            attendance = round(random.uniform(40, 95), 1)
            w.writerow([sid, attendance])
    print(f"Generated {filename}")


def generate_academics_csv(student_ids):
    """
    For /students/import-academics-csv
    Header:
    student_id,cgpa,backlogs,quiz_score_avg,bot_engagement_score,counselling_sessions
    """
    filename = "academics.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "student_id",
            "cgpa",
            "backlogs",
            "quiz_score_avg",
            "bot_engagement_score",
            "counselling_sessions",
        ])
        for sid in student_ids:
            cgpa = round(random.uniform(4.0, 9.5), 1)
            backlogs = random.choice([0, 0, 1, 2, 3])
            quiz_avg = round(random.uniform(30, 90), 1)
            engagement = round(random.uniform(0, 80), 1)
            sessions = random.choice([0, 0, 1, 2])
            w.writerow([sid, cgpa, backlogs, quiz_avg, engagement, sessions])
    print(f"Generated {filename}")


def generate_fees_csv(student_ids):
    """
    For /students/import-fees-csv
    Header:
    student_id,fees_pending,fees_amount_due
    """
    filename = "fees.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["student_id", "fees_pending", "fees_amount_due"])
        for sid in student_ids:
            fees_pending = random.choice(["true", "false", "false"])
            fees_amount = 0.0 if fees_pending == "false" else random.choice([15000, 25000, 35000])
            w.writerow([sid, fees_pending, fees_amount])
    print(f"Generated {filename}")


if __name__ == "__main__":
    ids = generate_student_ids(N_STUDENTS)
    generate_base_csv(ids)
    generate_attendance_csv(ids)
    generate_academics_csv(ids)
    generate_fees_csv(ids)
    print("Done. CSVs ready for upload.")
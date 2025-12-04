import csv
import random

OUTPUT_FILE = "base_students.csv"
NUM_STUDENTS = 1000  # change if you want more/less

departments = ["CSE", "IT", "ECE", "EEE", "ME", "CE"]
first_names = [
    "Aarav", "Diya", "Rohan", "Kriti", "Aditya", "Simran",
    "Manav", "Isha", "Neeraj", "Priya", "Rahul", "Sneha",
]
last_names = ["Mehta", "Sharma", "Verma", "Joshi", "Nair", "Kaur", "Rao", "Patel", "Singh", "Das"]

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
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
        "quiz_score_avg",
        "bot_engagement_score",
        "counselling_sessions",
    ])

    for i in range(1, NUM_STUDENTS + 1):
        sid = f"S{i:03d}"  # S001, S002, ...
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        name = f"{fn} {ln}"
        email = f"{fn.lower()}.{ln.lower()}{i}@example.com"
        phone = f"98765{i:05d}"[-10:]
        dept = random.choice(departments)
        semester = random.randint(1, 8)

        attendance = random.uniform(40, 95)
        cgpa = random.uniform(4.5, 9.5)
        backlogs = random.choice([0, 0, 0, 1, 2, 3, 4])  # more 0s
        fees_pending = random.choice(["true", "false", "false"])  # more "false"
        fees_amount_due = 0 if fees_pending == "false" else random.choice([5000, 8000, 12000, 15000, 20000])
        quiz_score_avg = random.uniform(40, 90)
        bot_engagement = random.uniform(20, 80)
        counselling_sessions = random.randint(0, 4)

        writer.writerow([
            sid,
            name,
            email,
            phone,
            dept,
            semester,
            round(attendance, 1),
            round(cgpa, 2),
            backlogs,
            fees_pending,
            fees_amount_due,
            round(quiz_score_avg, 1),
            round(bot_engagement, 1),
            counselling_sessions,
        ])

print(f"Generated {NUM_STUDENTS} students in {OUTPUT_FILE}")
import random
from datetime import datetime, timedelta
import pyodbc
import uuid

# DB connection
conn = pyodbc.connect(
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=LAMECKNYWIN10;"
    "Database=CitizenVoiceAI;"
    "UID=steveqaqaire;"
    "PWD=Iam_Marcus121212!;"
)
cursor = conn.cursor()

# Configuration
MONTHS = 12
COMPLAINTS_PER_MONTH = 5

categories = [
    "Water", "Roads", "Health", "Sanitation",
    "Electricity", "Education", "Security"
]

priorities = ["Normal", "High", "Urgent"]
statuses = ["Pending", "In Progress", "Resolved"]

locations = [
    "Kampala Central", "Makindye", "Kawempe",
    "Bukoto", "Kireka", "Gayaza", "Nansana"
]

descriptions = [
    "Issue reported by residents.",
    "Several complaints received.",
    "Affects daily community activities.",
    "Requires urgent government attention.",
    "Problem worsening according to locals."
]

def random_date(month_offset):
    """Generate a random date X months in the past."""
    today = datetime.utcnow()
    target_month = today - timedelta(days=30 * month_offset)
    day = random.randint(1, 28)
    return target_month.replace(day=day)

print("\n🔄 Inserting sample complaints...")

for m in range(1, MONTHS + 1):
    for i in range(COMPLAINTS_PER_MONTH):

        category = random.choice(categories)
        priority = random.choice(priorities)
        status = random.choice(statuses)
        location = random.choice(locations)
        description = random.choice(descriptions)
        created_at = random_date(m)

        resolved_at = None
        resolution_notes = None
        assigned_to = random.randint(2, 5)

        if status == "Resolved":
            resolved_at = created_at + timedelta(days=random.randint(1, 10))
            resolution_notes = "Issue resolved successfully"

        tracking_number = f"CMP-{uuid.uuid4().hex[:8].upper()}"

        cursor.execute("""
            INSERT INTO Complaints
            (citizen_id, ministry_id, district_id, category, description,
             location, priority, status, tracking_number, assigned_to,
             created_at, resolved_at, resolution_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            1, 1, 1,
            category, description, location,
            priority, status, tracking_number,
            assigned_to, created_at, resolved_at, resolution_notes
        ))

conn.commit()
conn.close()

print("\n✅ DONE! Random complaints inserted successfully.")

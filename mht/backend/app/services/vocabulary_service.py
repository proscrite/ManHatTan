import os
import pandas as pd
from app.database import engine, SessionLocal
from app.models import Base, User, UserCourse, UserVocabulary, generate_uuid
from app.security import get_password_hash

def test_database_import():
    print("1. Creating database tables in manhattan.db...")
    Base.metadata.create_all(bind=engine)
    
    # Open a database session
    db = SessionLocal()

    try:
        print("2. Creating a test User and Course...")
        # Check if user already exists to avoid errors on multiple runs
        test_user = db.query(User).filter(User.email == "pablo@test.com").first()
        if not test_user:
            hashed_password = get_password_hash("password123")
            test_user = User(email="pablo@test.com", name="Pablo", hashed_password=hashed_password)
            db.add(test_user)
            db.commit()
            db.refresh(test_user)

        # Check if Hebrew course exists for this user (don't overwrite other courses)
        test_course = db.query(UserCourse).filter(
            UserCourse.user_id == test_user.id,
            UserCourse.learning_language == "iw",
            UserCourse.ui_language == "en",
        ).first()
        if not test_course:
            test_course = UserCourse(
                user_id=test_user.id,
                learning_language="iw",
                ui_language="en",
                is_active=True,
            )
            db.add(test_course)
            db.commit()
            db.refresh(test_course)

        # print("3. Reading Schachnovelle.csv with Pandas...")
        print("3. Reading hebrew_db.csv with Pandas...")
        
        # Read CSV relative to this service file so CWD doesn't matter
        csv_path = os.path.join(os.path.dirname(__file__), "hebrew_db.csv")
        print(f"Reading CSV from: {csv_path}")
        # df = pd.read_csv("app/services/Schachnovelle.csv", encoding='utf-8')
        df = pd.read_csv(csv_path, encoding='utf-8')
                
        # 1. Convert DataFrame to a list of dictionaries (Extremely fast)
        records = df.to_dict(orient="records")

        # 2. Add necessary database IDs to those dictionaries
        for record in records:
            record['course_id'] = test_course.id
            record['id'] = generate_uuid() # From your models.py

        # 3. Bulk insert directly into the database (Bypasses the heavy ORM object creation)
        # Only insert if this course has no vocabulary yet to avoid duplicates
        existing = db.query(UserVocabulary).filter(UserVocabulary.course_id == test_course.id).first()
        if existing:
            print("-> Words already exist in database for this course. Skipping insert.")
        else:
            for record in records:
                record['course_id'] = test_course.id
                record['id'] = generate_uuid() # From your models.py

            if records:
                db.bulk_insert_mappings(UserVocabulary, records)
                db.commit()
                print(f"-> Inserted {len(records)} new words.")
            else:
                print("-> No records found in CSV. Nothing to insert.")

        print("\n5. Verification: Querying SQLite using pandas.read_sql!")
        # We use raw SQL here just for Pandas, but usually FastAPI uses the ORM
        sql_query = f"SELECT * FROM user_vocabulary WHERE course_id = '{test_course.id}' LIMIT 5;"
        
        # Read directly from the SQLite engine
        df_from_db = pd.read_sql(sql_query, engine)
        
        print("\n--- RESULTS FROM SQLITE ---")
        print(df_from_db[['word_ll', 'word_ul', 'p_recall', 'source_reference']])

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_database_import()
from datetime import datetime, timezone, timedelta
import os
import pandas as pd
from fsrs import State
from app.database import engine, SessionLocal
from app.models import Base, User, UserCourse, UserVocabulary, generate_uuid
from app.security import get_password_hash

def test_database_import():
    
    # Recreate missing tables (this will rebuild user_vocabulary with FSRS columns)
    Base.metadata.create_all(bind=engine)
    
    # Open a database session
    db = SessionLocal()
    print("1. Database session opened. Starting import process...")

    try:
        print("2. Creating a test User and Course...")
        # Check if user already exists to avoid errors on multiple runs
        test_user = db.query(User).filter(User.email == "pablogfr94@gmail.com").first()
        if not test_user:
            hashed_password = get_password_hash("ManhattanFTW")
            test_user = User(email="pablogfr94@gmail.com", hashed_password=hashed_password)
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
                cefr_level=1,
                fluency_index=0.0
            )
            db.add(test_course)
            db.commit()
            db.refresh(test_course)

        # print("3. Reading Schachnovelle.csv with Pandas...")
        print("3. Reading hebrew_db.csv with Pandas...")
        
        csv_path = os.path.join(os.path.dirname(__file__), "hebrew_db.csv")
        print(f"Reading CSV from: {csv_path}")
        # df = pd.read_csv("app/services/Schachnovelle.csv", encoding='utf-8')
        df = pd.read_csv(csv_path, encoding='utf-8')
                
        # 1. Convert DataFrame to a list of dictionaries (Extremely fast)
        records = df.to_dict(orient="records")

        # Define legacy columns to purge after mapping
        legacy_columns = [
            'p_recall', 'history_seen', 'history_correct', 'session_seen', 
            'session_correct', 'mdt_history', 'mdt_correct', 'mrt_history', 
            'mrt_correct', 'wdt_history', 'wdt_correct', 'wrt_history', 
            'wrt_correct', 'speed'
        ]

        # 2. Transform the records to match the new FSRS + JSON Schema
        formatted_records = []
        for record in records:
            # Generate Base IDs
            record['course_id'] = test_course.id
            record['id'] = generate_uuid()
            
            # Initialize FSRS Base State (0 = New Card)
            record['fsrs_state'] = State.New.value
            record['next_review_at'] = datetime.now(timezone.utc)
    
            record['fsrs_difficulty'] = 0.0
            record['fsrs_stability'] = 0.0
            record['fsrs_last_review'] = datetime.now(timezone.utc) - timedelta(days=1)  
            record['reps'] = 0
            record['lapses'] = 0
            
            # Consolidate legacy modality stats into the new JSON field
            record['modality_stats'] = {
                "mdt": {"seen": record.get('mdt_history', 0), "correct": record.get('mdt_correct', 0)},
                "mrt": {"seen": record.get('mrt_history', 0), "correct": record.get('mrt_correct', 0)},
                "wdt": {"seen": record.get('wdt_history', 0), "correct": record.get('wdt_correct', 0)},
                "wrt": {"seen": record.get('wrt_history', 0), "correct": record.get('wrt_correct', 0)}
            }

            # Strip out legacy columns so SQLAlchemy doesn't crash on unknown kwargs
            for col in legacy_columns:
                record.pop(col, None)
                
            formatted_records.append(record)
        print(f"-> Transformed {len(formatted_records)} records to match FSRS schema.")

        # 3. Bulk insert directly into the database
        existing = db.query(UserVocabulary).filter(UserVocabulary.course_id == test_course.id).first()
        if existing:
            print("-> Words already exist in database for this course. Skipping insert.")
        else:
            if formatted_records:
                db.bulk_insert_mappings(UserVocabulary, formatted_records)
                db.commit()
                print(f"-> Inserted {len(formatted_records)} new words.")
            else:
                print("-> No records found in CSV. Nothing to insert.")

        print("\n5. Verification: Querying SQLite using pandas.read_sql!")
        # We use raw SQL here just for Pandas, but usually FastAPI uses the ORM
        sql_query = f"SELECT * FROM user_vocabulary WHERE course_id = '{test_course.id}' LIMIT 5;"
        
        # Read directly from the SQLite engine
        df_from_db = pd.read_sql(sql_query, engine)
        
        print("\n--- RESULTS FROM SQLITE ---")
        print(df_from_db[['word_ll', 'word_ul', 'modality_stats', 'source_reference']])

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_database_import()
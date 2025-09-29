import pandas as pd
import json
from sqlalchemy import create_engine, text
import time

engine = create_engine('postgresql://yourname:password@localhost:5432/dbname')

dataset_path = 'data/test.jsonl'
chunk_size = 500  

print("Start processing test.jsonl..")

# --- STEP 0: Table initiation ---
# 테이블 데이터 초기화 하기 위한 로직
# with engine.begin() as conn:
#     conn.execute(text("TRUNCATE TABLE test_cases RESTART IDENTITY CASCADE;"))
#     conn.execute(text("TRUNCATE TABLE problems RESTART IDENTITY CASCADE;"))
# print("Database truncated and ready.")

with pd.read_json(dataset_path, lines=True, chunksize=chunk_size) as reader:
    chunk_idx = 0
    for chunk in reader:
        chunk_idx += 1
        start_time = time.time()
        print(f"\nProcessing chunk {chunk_idx} ({len(chunk)} rows)")

        # --- STEP 1: Prepare problems rows ---
        problem_rows = []
        for _, row in chunk.iterrows():
            problem_rows.append({
                "problem_id": int(row['id']),
                "question": row["question"],
                "difficulty": row.get("difficulty", None),
                "url": row.get("url", None),
                "starter_code": row.get("starter_code", None),
                "solutions": json.dumps(row.get("solutions", [])),
                "dataset_type": "test"
            })
        problems_df = pd.DataFrame(problem_rows)

        # --- STEP 2: Insert problems safely ---
        try:
            with engine.begin() as conn:
                for _, row in problems_df.iterrows():
                    conn.execute(text("""
                        INSERT INTO problems (problem_id, question, difficulty, url, starter_code, solutions, dataset_type)
                        VALUES (:problem_id, :question, :difficulty, :url, :starter_code, :solutions, :dataset_type)
                        ON CONFLICT (problem_id, dataset_type) DO NOTHING;
                    """), row.to_dict())
            print(f"Problems inserted/updated for chunk {chunk_idx}")
        except Exception as e:
            print(f"Error inserting problems for chunk {chunk_idx}: {e}")
            continue

        # --- STEP 3: Map problem_id -> DB id ---
        try:
            with engine.connect() as conn:
                source_ids = tuple(problems_df['problem_id'].tolist())
                if not source_ids:
                    continue
                query = text("""
                    SELECT id, problem_id
                    FROM problems
                    WHERE problem_id = ANY(:source_ids) AND dataset_type='test';
                """)
                result = conn.execute(query, {"source_ids": list(source_ids)})
                id_map = {row['problem_id']: row['id'] for row in result.mappings()}
        except Exception as e:
            print(f"Error retrieving problem IDs for chunk {chunk_idx}: {e}")
            continue

        # --- STEP 4: Prepare test_cases rows ---
        test_cases_rows = []
        for _, row in chunk.iterrows():
            db_problem_id = id_map.get(row['id'])
            if not db_problem_id:
                continue

            io_data = row.get("input_output", {})
            if isinstance(io_data, str):
                io_data = json.loads(io_data)
            inputs = io_data.get("inputs", [])
            outputs = io_data.get("outputs", [])

            if len(inputs) != len(outputs):
                print(f"Problem {row['id']} has mismatched inputs/outputs ({len(inputs)} / {len(outputs)})")
                continue

            for inp, outp in zip(inputs, outputs):
                test_cases_rows.append({
                    "problem_id": db_problem_id,
                    "input_data": json.dumps(inp),
                    "output_data": json.dumps(outp)
                })

        # --- STEP 5: Insert test_cases in smaller batches ---
        if test_cases_rows:
            batch_size = 200  # 너무 커서 멈추는 걸 방지
            for i in range(0, len(test_cases_rows), batch_size):
                batch = test_cases_rows[i:i+batch_size]
                try:
                    with engine.begin() as conn:
                        pd.DataFrame(batch).to_sql(
                            name="test_cases",
                            con=conn,
                            if_exists="append",
                            index=False,
                            method="multi"
                        )
                    print(f"Inserted {len(batch)} test_cases (batch {i//batch_size + 1})")
                except Exception as e:
                    print(f"Error inserting test_cases batch {i//batch_size + 1}: {e}")

        print(f"Chunk {chunk_idx} processed in {time.time() - start_time:.2f} seconds")

print("\nAll chunks processed successfully!")

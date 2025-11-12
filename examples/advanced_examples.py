"""
PyProfiler Examples - Real-world use cases
"""

# ============================================================================
# Example 1: Web Application (Flask)
# ============================================================================

from flask import Flask, request
from pyprofiler import Profiler, time_block

app = Flask(__name__)

@app.before_request
def start_profiler():
    request.profiler = Profiler()
    request.profiler_ctx = request.profiler.time("request_handler")
    request.profiler_ctx.__enter__()

@app.after_request
def end_profiler(response):
    request.profiler_ctx.__exit__(None, None, None)
    request.profiler.print_summary()
    return response

@app.route("/users")
def get_users():
    with request.profiler.time("database_query"):
        users = db.query("SELECT * FROM users")
    
    with request.profiler.time("serialization"):
        return jsonify(users)


# ============================================================================
# Example 2: Data Pipeline
# ============================================================================

from pyprofiler import time_block, checkpoint

def process_data_pipeline(data_file):
    with time_block("data_pipeline"):
        # Extract
        with time_block("extract", source=data_file):
            data = pd.read_csv(data_file)
            checkpoint("data_loaded", rows=len(data))
        
        # Transform
        with time_block("transform"):
            data = data.dropna()
            data = data.apply_transformations()
            checkpoint("transform_complete", rows=len(data))
        
        # Load
        with time_block("load", destination="database"):
            data.to_sql("processed_data", engine)
            checkpoint("load_complete", rows=len(data))
    
    from pyprofiler import print_summary
    print_summary()


# ============================================================================
# Example 3: API Integration
# ============================================================================

import requests
from pyprofiler import time_block

class APIClient:
    def __init__(self):
        self.base_url = "https://api.example.com"
    
    def fetch_users(self):
        with time_block("api_call", endpoint="/users", method="GET"):
            response = requests.get(f"{self.base_url}/users")
            return response.json()
    
    def create_user(self, data):
        with time_block("api_call", endpoint="/users", method="POST"):
            response = requests.post(f"{self.base_url}/users", json=data)
            return response.json()


# ============================================================================
# Example 4: Machine Learning
# ============================================================================

from sklearn.ensemble import RandomForestClassifier
from pyprofiler import time_block, checkpoint

def train_model(X_train, y_train, X_test, y_test):
    with time_block("ml_pipeline"):
        # Training
        with time_block("model_training", model="random_forest"):
            model = RandomForestClassifier(n_estimators=100)
            model.fit(X_train, y_train)
            checkpoint("training_complete", features=X_train.shape[1])
        
        # Evaluation
        with time_block("model_evaluation"):
            score = model.score(X_test, y_test)
            checkpoint("evaluation_complete", accuracy=score)
        
        # Inference
        with time_block("model_inference", batch_size=len(X_test)):
            predictions = model.predict(X_test)
    
    from pyprofiler import print_summary
    print_summary()


# ============================================================================
# Example 5: Async Operations
# ============================================================================

import asyncio
from pyprofiler import time_block, checkpoint

async def fetch_data_async():
    urls = ["url1", "url2", "url3"]
    
    with time_block("async_operations"):
        tasks = []
        for i, url in enumerate(urls):
            with time_block(f"create_task_{i}", url=url):
                task = asyncio.create_task(fetch_url(url))
                tasks.append(task)
        
        with time_block("await_all"):
            results = await asyncio.gather(*tasks)
            checkpoint("all_fetched", count=len(results))
    
    from pyprofiler import print_summary
    print_summary()

async def fetch_url(url):
    with time_block("http_request", url=url):
        await asyncio.sleep(1)  # Simulate HTTP request
        return f"data from {url}"


# ============================================================================
# Example 6: Database Operations
# ============================================================================

from pyprofiler import get_profiler

profiler = get_profiler()

@profiler.track
def complex_query():
    # This function will be automatically timed
    return db.execute("""
        SELECT users.*, COUNT(orders.id) as order_count
        FROM users
        LEFT JOIN orders ON users.id = orders.user_id
        GROUP BY users.id
    """)

@profiler.track
def batch_insert(records):
    db.bulk_insert("users", records)


# ============================================================================
# Example 7: CLI Application with Optional Profiling
# ============================================================================

import click
from pyprofiler import Profiler, time_block

@click.command()
@click.option("--profile", is_flag=True, help="Enable profiling")
def main(profile):
    if profile:
        profiler = Profiler()
        
        with profiler.time("cli_execution"):
            run_application()
        
        profiler.print_summary()
        profiler.export_json("profile.json")
    else:
        run_application()

def run_application():
    # Your application code
    pass


# ============================================================================
# Example 8: Class-based Profiling
# ============================================================================

from pyprofiler import Profiler

class DataProcessor:
    def __init__(self):
        self.profiler = Profiler()
    
    def process(self, data):
        with self.profiler.time("full_process"):
            self._validate(data)
            self._transform(data)
            self._save(data)
        
        return self.profiler.get_stats()
    
    def _validate(self, data):
        with self.profiler.time("validate"):
            # Validation logic
            pass
    
    def _transform(self, data):
        with self.profiler.time("transform"):
            # Transformation logic
            pass
    
    def _save(self, data):
        with self.profiler.time("save"):
            # Save logic
            pass


# ============================================================================
# Example 9: Context-specific Profiling
# ============================================================================

from pyprofiler import Profiler

def process_with_context(data, context):
    profiler = Profiler()
    
    with profiler.time("processing", **context):
        # Process with context metadata
        result = process(data)
    
    # Export with context in filename
    profiler.export_json(f"profile_{context['user_id']}.json")
    
    return result


# ============================================================================
# Example 10: Disable in Production
# ============================================================================

import os
from pyprofiler import Profiler

# Enable profiling only in dev/staging
profiler = Profiler(enabled=os.getenv("ENABLE_PROFILING") == "true")

with profiler.time("operation"):
    # This has zero overhead if profiling is disabled
    expensive_operation()


# ============================================================================
# Run Examples
# ============================================================================

if __name__ == "__main__":
    print("Running Example 2: Data Pipeline")
    # Uncomment to run:
    # process_data_pipeline("data.csv")
    
    print("\nRunning Example 5: Async Operations")
    # asyncio.run(fetch_data_async())
    
    print("\nSee other examples above!")
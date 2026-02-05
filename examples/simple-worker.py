import time
import random
from maos_agent import MaosAgent, SpotInterruptionError

# 1. Initialize
agent = MaosAgent(service_name="stock-analyst", version="v1.2")

# 2. Define a Tool (Auto-tracked)
@agent.tool(name="google_search")
def search(query):
    if random.random() < 0.1:
        raise Exception("Network Error") # Will show as red in Grafana
    return "Result"

# 3. The Worker Loop
def process_job():
    print("Starting job...")
    
    # Track duration, steps, and success automatically
    with agent.task("daily_report") as task:
        for i in range(5):
            # Check if Spot Instance is dying
            agent.check_health() 
            
            # Simulate "Thinking"
            task.step() 
            search("Apple Stock")
            time.sleep(1)

if __name__ == "__main__":
    try:
        process_job()
    except SpotInterruptionError:
        print("🚨 SAVING STATE TO REDIS BEFORE DEATH...")
        # Checkpoint logic here
        exit(0)
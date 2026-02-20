import os
import json
from datetime import datetime

class BucketStore:
    def __init__(self, root_dir="bucket/artifacts"):
        self.root_dir = root_dir
        os.makedirs(self.root_dir, exist_ok=True)

    def persist_artifact(self, trace_id, category, data):
        """
        Persists a deterministic artifact of a decision or event.
        Category can be 'success' or 'failure'.
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.root_dir}/{category}_{trace_id}_{timestamp}.json"
        
        artifact = {
            "metadata": {
                "trace_id": trace_id,
                "category": category,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            },
            "data": data
        }
        
        with open(filename, "w") as f:
            json.dump(artifact, f, indent=2)
        return filename

if __name__ == "__main__":
    # Test bucket
    bs = BucketStore()
    path = bs.persist_artifact("test-trace", "success", {"msg": "Initial bucket test"})
    print(f"Artifact persisted at {path}")

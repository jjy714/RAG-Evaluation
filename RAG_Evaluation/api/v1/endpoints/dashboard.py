# from fastapi import APIRouter


# router = APIRouter()


async def dashboard_stream_generator():
    """
    A generator that yields SSE events for the dashboard.
    """
    while True:
        # In a real application, you would fetch the actual status
        # of the running evaluations and send updates.
        # For this example, we'll just send a ping.
        
        # Create a JSON object with the current status of all evaluations
        dashboard_data = {
            "evaluations": [
                {"id": eid, "status": evals["status"]}
                for eid, evals in evaluations.items()
            ]
        }
        
        yield f"data: {json.dumps(dashboard_data)}\n\n"
        await asyncio.sleep(1)


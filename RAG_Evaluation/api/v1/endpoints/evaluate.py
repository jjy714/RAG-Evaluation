


# async def start_evaluation(request: EvaluationRequest, background_tasks: BackgroundTasks):
#     """
#     Starts a new evaluation as a background task.
#     """
#     evaluation_id = str(uuid.uuid4())
#     evaluations[evaluation_id] = {"status": "pending", "result": None}
#     background_tasks.add_task(run_evaluation, evaluation_id, request)
#     return {"evaluation_id": evaluation_id}

# @router.get("/evaluate/{evaluation_id}", response_model=EvaluationStatusResponse)
# def get_evaluation_status(evaluation_id: str):
#     """
#     Checks the status and results of an evaluation.
#     """
#     evaluation = evaluations.get(evaluation_id)
#     if not evaluation:
#         raise HTTPException(status_code=404, detail="Evaluation not found")
#     return evaluation

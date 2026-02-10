from fastapi import FastAPI
from backend.api.score import score_account

app = FastAPI(title="UPI Mule Detection MVP")

@app.get("/score/{account_id}")
def score(account_id: str):
    return score_account(account_id)
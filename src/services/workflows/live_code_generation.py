from datetime import datetime
from src.dao.live_code import LiveCodeDAO

def generate_live_code():
    code_generation_time = datetime.now()
    live_code = code_generation_time.microsecond
    status = "not_started"
    LiveCodeDAO.add_live_code(live_code = live_code, status = status, code_generation_time = code_generation_time)
    print(f"LIVE CODE GENERATED : {live_code}")

if __name__ == "__main__":
    generate_live_code()

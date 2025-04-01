from datetime import datetime
from src.dao.live_code import LiveCodeDAO

def generate_live_code():
    code_generation_time = datetime.now()
    live_code = code_generation_time.microsecond
    status = "not_started"
    live_code_str = str(live_code)
    live_code_str_zfilled = live_code_str.zfill(6)
    LiveCodeDAO.add_live_code(live_code = live_code_str_zfilled, status = status, code_generation_time = code_generation_time)
    print(f"LIVE CODE GENERATED : {live_code_str_zfilled}")

if __name__ == "__main__":
    generate_live_code()

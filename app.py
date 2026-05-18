from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import traceback
import sys
from io import StringIO
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def execute_python_code(code: str):
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        exec(code)
        output = sys.stdout.getvalue()
        return {"success": True, "output": output}

    except Exception:
        output = traceback.format_exc()
        return {"success": False, "output": output}

    finally:
        sys.stdout = old_stdout

def analyze_error(traceback_text: str):
    matches = re.findall(r'line (\d+)', traceback_text)
    return sorted(list(set(int(x) for x in matches)))

@app.post("/code-interpreter")
async def code_interpreter(payload: dict):

    code = payload.get("code", "")

    execution = execute_python_code(code)

    if execution["success"]:
        return {
            "error": [],
            "result": execution["output"]
        }

    return {
        "error": analyze_error(execution["output"]),
        "result": execution["output"]
    }
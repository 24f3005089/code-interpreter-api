from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
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

class CodeRequest(BaseModel):
    code: str

class CodeResponse(BaseModel):
    error: List[int]
    result: str

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
    lines = [int(x) for x in matches]
    return sorted(list(set(lines)))

@app.post("/code-interpreter", response_model=CodeResponse)
def code_interpreter(req: CodeRequest):

    execution = execute_python_code(req.code)

    if execution["success"]:
        return {
            "error": [],
            "result": execution["output"]
        }

    return {
        "error": analyze_error(execution["output"]),
        "result": execution["output"]
    }
from fastapi import HTTPException
import json

def read_file_as_text(file_path):
    try:
        with open(file_path, 'r') as file:
            data = file.read()
        return data
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File {file_path} not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading {file_path}: {e}")
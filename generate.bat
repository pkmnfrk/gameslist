@ECHO OFF

IF NOT EXIST venv (
    py -3 -m venv venv
    call venv\scripts\activate
    python -m pip install -U pip
    pip install -r requirements.txt
) ELSE (
    call venv\scripts\activate
)

python schedule.py
@REM python keys.py

django webapp

in case pip not found:
    python get-pip.py

run:

    uv venv book_borrower_venv
    python -m ensurepip --upgrade
    pip install -r requirements.txt
    docker compose up -d
    python manage.py migrate
    python manage.py runserver
    

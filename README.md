django webapp

run:

    python -m venv book_borrower_venv
    pip install -r requirements.txt
    docker compsoe up -d
    python manage.py migrate
    python manage.py runserver
    

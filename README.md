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
for schema generation run:

    python manage.py spectacular --color --file schema.yml
    docker run -d -p 8080:8080 -e SWAGGER_JSON=/schema.yml -v ${PWD}/schema.yml:/schema.yml swaggerapi/swagger-ui

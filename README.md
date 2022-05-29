# Assignment Ticket Store

## How to run the app

1. Install dependencies

```
pip install -r requirements.txt
```

2. Run server (`app.py`)

> This is going to populate a test database with some mock data. The server must be listening on port `5000`.

```
FLASK_ENV=development FLASK_APP=app flask run

$ Running on http://127.0.0.1:5000
```

3. Use CLI to purchase tickets (`cli.py`)

```
python3 cli.py
```

4. The output should look like this:

<p align="center">
  <img src="https://raw.githubusercontent.com/macmillen/python-event-api/master/output.png" width="450" title="hover text">
</p>


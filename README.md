# Description
Reads two given html source codes into BeautifulSoup objects. Extracts features and predicts whether one html source code is a phishing attempt masquerading as the other.

# How to Use
Install requirements with

```
pip install -r requirements.txt
```

Navigate to the relevant iteration in the 'iterations' directory and run main.py for command line results or web.py for web app.

For command line results,
python3 iterations/<number>/main.py --html1 <html1_path> --html2 <html2_path'>
Where 'html1_path' and 'html2_path' are file paths to two html source codes to be compared against each other.

Example,
```
python3 iterations/3/main.py --html1 phish_test/original.html --html2 phish_test/phish.html
```

For web app, type in terminal,
```
flask --app iterations/3/web run
```

Ctrl+click on link in terminal to open web app.

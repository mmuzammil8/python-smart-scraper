from flask import Flask, request, render_template
import csv

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    results = []
    if request.method == 'POST':
        keyword = request.form['keyword']
        with open('output/linkedin_contacts.csv', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            results = [row for row in reader if keyword.lower() in row['title'].lower()]
    return render_template('index.html', results=results)

if __name__ == "__main__":
    app.run(debug=True)

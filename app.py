from flask import Flask, request, render_template
import os
import spacy
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

nlp = spacy.load("en_core_web_sm")

def parse_resume(text):
    doc = nlp(text)
    name = None
    email = None
    phone = None
    skills = []

    for ent in doc.ents:
        if ent.label_ == "PERSON" and not name:
            name = ent.text
        elif ent.label_ == "EMAIL":
            email = ent.text
        elif ent.label_ == "PHONE_NUMBER":
            phone = ent.text

    for token in doc:
        if token.pos_ == "NOUN" and token.text.lower() not in skills:
            skills.append(token.text.lower())

    return {
        "Name": name,
        "Email": email,
        "Phone": phone,
        "Skills": list(set(skills))[:10]  # limit to top 10 unique skills
    }

@app.route('/', methods=['GET', 'POST'])
def index():
    parsed_data = {}
    error = ""
    if request.method == 'POST':
        if 'resume' not in request.files:
            error = "No file part"
        file = request.files['resume']
        if file.filename == '':
            error = "No selected file"
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
                parsed_data = parse_resume(text)
    return render_template('index.html', parsed_data=parsed_data, error=error)

if __name__ == '__main__':
    app.run(debug=True)
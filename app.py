from flask import Flask, render_template, request, redirect, jsonify
import requests
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expenses
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  amount REAL NOT NULL,
                  category TEXT NOT NULL)''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('SELECT * FROM expenses')
    expenses = c.fetchall()
    conn.close()
    return render_template('index.html', expenses=expenses)

@app.route('/add', methods=['POST'])
def add_expense():
    title = request.form['title']
    amount = request.form['amount']
    category = request.form['category']
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('INSERT INTO expenses (title, amount, category) VALUES (?, ?, ?)',
              (title, amount, category))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/delete/<int:id>')
def delete_expense(id):
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('DELETE FROM expenses WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/')
@app.route('/suggest-category', methods=['POST'])
def suggest_category():
    try:
        title = request.json.get('title', '')
        
        url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}'
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f'You are an expense categorizer. Given this expense title: "{title}", reply with ONLY one word from this list: Food, Transport, Study, Entertainment, Other. No explanation, just the single category word.'
                }]
            }]
        }
        
        response = requests.post(url, json=payload)
        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)
        data = response.json()
        category = data['candidates'][0]['content']['parts'][0]['text'].strip()
        
        if category not in ['Food', 'Transport', 'Study', 'Entertainment', 'Other']:
            category = 'Other'
        
        return jsonify({'category': category})
    
    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({'category': 'Other', 'error': str(e)})
if __name__ == '__main__':
    init_db()
    app.run(debug=True)

from flask import Flask, request, render_template, jsonify, redirect, url_for
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/company_policies'
mongo = PyMongo(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    user_email = request.form.get('email', '').strip()
    query = request.form.get('query', '').lower()
    user_exists = False
    response = None

    if request.method == 'POST':
        if user_email:
            # Check if user exists
            user = mongo.db.users.find_one({"email": user_email})
            user_exists = True

            if user:
                # Update chat history
                mongo.db.users.update_one(
                    {"email": user_email},
                    {"$push": {"chat_history": {"query": query, "response": get_policy_response(query)}}}
                )
            else:
                # Create new user and save chat history
                mongo.db.users.insert_one({
                    "email": user_email,
                    "chat_history": [{"query": query, "response": get_policy_response(query)}]
                })

            response = get_policy_response(query)

        return render_template('index.html', response=response, query=query, email=user_email, user_exists=user_exists)

    return render_template('index.html', user_exists=False)

@app.route('/add_policy', methods=['GET', 'POST'])
def add_policy():
    if request.method == 'POST':
        name = request.form.get('name', '')
        details = request.form.get('details', '')
        if name and details:
            mongo.db.policies.insert_one({"name": name, "details": details})
        return redirect(url_for('add_policy'))

    return render_template('add_policy.html')

@app.route('/history/<email>', methods=['GET'])
def history(email):
    user = mongo.db.users.find_one({"email": email})
    if user:
        return jsonify(user['chat_history'])
    return jsonify([])

def get_policy_response(query):
    response = mongo.db.policies.find_one({"name": {"$regex": query, "$options": "i"}})
    return response['details'] if response else "I'm sorry, I couldn't find information on that topic."

if __name__ == '__main__':
    app.run(debug=True)

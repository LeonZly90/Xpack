from flask import Flask, render_template_string, request

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    search_result = None
    if request.method == 'POST':
        search_query = request.form.get('search')
        search_result = f"You searched for: {search_query}"

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>X-Pack Demo</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
            h1 { color: #333; }
            form { margin-bottom: 20px; }
            input[type="text"] { padding: 5px; width: 200px; }
            input[type="submit"] { padding: 5px 10px; }
            #result { color: #007bff; }
        </style>
    </head>
    <body>
        <h1>Welcome to X-Pack Demo</h1>
        <form method="post">
            <input type="text" name="search" placeholder="Enter search term">
            <input type="submit" value="Search">
        </form>
        {% if search_result %}
        <p id="result">{{ search_result }}</p>
        {% endif %}
    </body>
    </html>
    """
    return render_template_string(html, search_result=search_result)

if __name__ == '__main__':
    app.run(debug=True)
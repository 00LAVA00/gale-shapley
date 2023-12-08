from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/setup', methods=['POST'])
def setup():
    num_pairs = int(request.form['num_pairs'])
    return render_template('setup.html', num_pairs=num_pairs)

@app.route('/preferences', methods=['POST'])
def preferences():
    num_pairs = int(request.form['num_pairs'])

    # Create arrays to store male and female preferences
    male_preferences = []
    female_preferences = []

    for i in range(num_pairs):
        male_key = f"male_preference{i}"
        female_key = f"female_preference{i}"

        # Get preferences from the form data
        male_preference = request.form.get(male_key, '').split(',')
        female_preference = request.form.get(female_key, '').split(',')

        # Convert preferences to integers and append to arrays
        male_preferences.append(list(map(int, male_preference)))
        female_preferences.append(list(map(int, female_preference)))

    # Now, male_preferences and female_preferences hold the input preferences
    # You can use these arrays as needed, for example, pass them to your matching algorithm

    return render_template('preferences.html', num_pairs=num_pairs)
if __name__ == '__main__':
    app.run(debug=True)

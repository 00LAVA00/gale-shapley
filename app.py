from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import numpy as np
from collections import Counter
from copy import copy

app = Flask(__name__)

def create_matching_dataframes(num_boys, boys_preference_matrix, girls_preference_matrix):
    # Lists of men and women
    man_list = [('M' + str(i+1)) for i in range(num_boys)]
    women_list = [('F' + str(i+1)) for i in range(num_boys)]

    # Creating DataFrame for women's preferences
    women_df = pd.DataFrame({women_list[i]: girls_preference_matrix[i] for i in range(len(women_list))})
    women_df.index = man_list

    # Creating DataFrame for men's preferences
    man_df = pd.DataFrame({women_list[i]: [row[i] for row in boys_preference_matrix] for i in range(len(women_list))})
    man_df.index = man_list

    return women_df, man_df,women_list,man_list


def gale_shapley(women_df, man_df, women_list, man_list):
    # dict to control which women each man can make proposals
    women_available = {man: copy(women_list) for man in man_list}
    # waiting list of men that were able to create a pair on each iteration
    waiting_list = []
    # dict to store created pairs
    proposals = {}
    # variable to count the number of iterations
    count = 0

    while len(waiting_list) < len(man_list):
        for man in man_list:
            if man not in waiting_list:
                women = women_available[man]
                best_choice = min(women, key=lambda w: man_df.loc[man, w])
                proposals[(man, best_choice)] = (man_df.loc[man, best_choice], women_df.loc[man, best_choice])

        overlays = Counter([key[1] for key in proposals.keys()])

        for women in overlays.keys():
            if overlays[women] > 1:
                pairs_to_drop = sorted({pair: proposals[pair] for pair in proposals.keys() if women in pair}.items(),
                                       key=lambda x: x[1][1])[1:]

                for p_to_drop in pairs_to_drop:
                    del proposals[p_to_drop[0]]
                    _women = copy(women_available[p_to_drop[0][0]])
                    _women.remove(p_to_drop[0][1])
                    women_available[p_to_drop[0][0]] = _women

        waiting_list = [man[0] for man in proposals.keys()]
        count += 1

    return proposals,count

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
    print("Male Preferences:")
    print(male_preferences)
    print("Female Preferences:")
    print(female_preferences)

    #converting the input matrix taken form the webpage into DataFrames using "create_matching_dataframes" func
    women_df, man_df,women_list,man_list= create_matching_dataframes(num_pairs,male_preferences,female_preferences) 
    print("Women's Preferences:")
    print(women_df)
    print("Man's Preferences:")
    print(man_df)

    
    #calling gale_shapley function to implement the algorithm
    matched_pairs,count = gale_shapley(women_df, man_df,women_list, man_list)
    #printing mathed_pairs
    print(matched_pairs)
    print(count)

    # Convert DataFrames to HTML tables
    women_html_table = women_df.to_html(classes='table  table-dark table-bordered table-striped', index=True)
    man_html_table = man_df.to_html(classes='table  table-dark table-bordered table-striped', index=True)

    return render_template('preferences.html', num_pairs=num_pairs, male_preferences=male_preferences,
                           female_preferences=female_preferences, matched_pairs=matched_pairs,
                           women_html_table=women_html_table, man_html_table=man_html_table,
                           women_list=women_list, man_list=man_list)





if __name__ == '__main__':
    app.run(debug=True)

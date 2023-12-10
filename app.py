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

    return women_df, man_df, women_list, man_list



def gale_shapley(women_df, man_df, women_list, man_list):
    xxx=""
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

        # Print information for this iteration
        a=f"Iteration {count}:"
        xxx+=a+"\n"
        for pair, values in proposals.items():
            b=f"{pair[0]} proposes to {pair[1]} with preference values {values}"
            xxx+=b+"\n"

        overlays = Counter([key[1] for key in proposals.keys()])
        a=f"Overlapping proposals: {overlays}"
        xxx+=a+"\n"

        for woman, count in overlays.items():
            if count > 1:
                c=f"Conflict for {woman}. Choosing the best proposal."
                xxx+=c+"\n"
        
        #print(f"Waiting list: {', '.join(waiting_list)}")
        #print("Women available:")
        # ll=f"Waiting list: {', '.join(waiting_list)}"
        # xxx+=ll+"\n" + "Women available:\n"
        # for man, women in women_available.items():
        #     xy=f"{man}: {', '.join(women)}"
        #     xxx+=xy+"\n"      
        # print("\n")
    #print(xxx)
    iteration_states = []

    while len(waiting_list) < len(man_list):
        iteration_state = {
            "proposals": dict(proposals),
            "waiting_list": list(waiting_list),
            "women_available": dict(women_available),
            "reasons": {},  # Track reasons for each proposal
        }

        for pair, values in proposals.items():
            male, female = pair
            iteration_state["reasons"][pair] = {
                "preference_values": values,
                "male_preferences": list(man_df.loc[male]),
                "female_preferences": list(women_df.loc[female]),
            }

        iteration_states.append(iteration_state)
        print(iteration_states)
    return dict(proposals), xxx

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
        male_preferences_row = []
        female_preferences_row = []

        for j in range(num_pairs):
            male_key = f"male_preference{i}_{j}"
            female_key = f"female_preference{i}_{j}"

            male_preference = int(request.form.get(male_key, 0))  # assuming 0 is a default value if not selected
            female_preference = int(request.form.get(female_key, 0))  # assuming 0 is a default value if not selected

            male_preferences_row.append(male_preference)
            female_preferences_row.append(female_preference)

        male_preferences.append(male_preferences_row)
        female_preferences.append(female_preferences_row)
    # Now, male_preferences and female_preferences hold the input preferences
    # You can use these arrays as needed, for example, pass them to your matching algorithm
    # print("Male Preferences:")
    # print(male_preferences)
    # print("Female Preferences:")
    # print(female_preferences)

    #converting the input matrix taken form the webpage into DataFrames using "create_matching_dataframes" func
    women_df, man_df,women_list,man_list= create_matching_dataframes(num_pairs,male_preferences,female_preferences) 
    # print("Women's Preferences:")
    # print(women_df)
    # print("Man's Preferences:")
    # print(man_df)

    
    #calling gale_shapley function to implement the algorithm
    matched_pairs, iteration_states = gale_shapley(women_df, man_df,women_list, man_list)
    #printing mathed_pairs
    # print(matched_pairs)
    # print("Iteration States:\n ",iteration_states)
 
    
    iteration_states_lines = []
    for line in iteration_states.split("\n"):
        if line.startswith("Iteration"):
            iteration_states_lines.append("<p style='padding-top: 10px;'><strong>" + line + "</strong></p>")
        else:
            iteration_states_lines.append("<p>&emsp;" + line + "</p>")

    # Join the lines into a single string
    iteration_states_html = "\n".join(iteration_states_lines)


    # Convert DataFrames to HTML tables
    women_html_table = women_df.to_html(classes='table  table-info table-bordered table-striped rounded-3', index=True)
    man_html_table = man_df.to_html(classes='table  table-info table-bordered table-striped rounded-3', index=True)

    return render_template('preferences.html', num_pairs=num_pairs, male_preferences=male_preferences,
                           female_preferences=female_preferences, matched_pairs=matched_pairs,
                           women_html_table=women_html_table, man_html_table=man_html_table,
                           women_list=women_list, man_list=man_list,iteration_states=iteration_states_html)





if __name__ == '__main__':
    app.run(debug=True)

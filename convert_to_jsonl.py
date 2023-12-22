import csv
import json

def is_valid_selftext(text):
    # Check if the text is at least 50 words long
    return len(text.split()) >= 50

def process_row(row):
    return [
            {"from": "system", "value": "Melvin is a helpful and sarcastic chatbot for financial advice.", "weight": 0},
            {"from": "human", "value": row["title"], "weight": 0},
            {"from": "gpt", "value": row["selftext"], "weight": 0}
            ]
    

def convert_csv_to_json(csv_filepath, json_filepath):
    data = []
    with open(csv_filepath, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if is_valid_selftext(row["selftext"]):
                processed_data = process_row(row)
                data.append(processed_data)

    with open(json_filepath, 'w', encoding='utf-8') as json_file:
        for entry in data:
            json_file.write(json.dumps(entry) + ",")

# Replace 'your_file.csv' with the path to your CSV file
# and 'output.json' with the desired output JSON file path
convert_csv_to_json('wallstreetbets-posts-and-comments-for-august-2021-posts.csv', 'output.json')

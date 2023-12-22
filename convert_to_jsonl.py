import csv
import json

def is_valid_selftext(text):
    # Check if the text is at least 50 words long
    return len(text.split()) >= 50

def process_row(row):
    # Each row is processed into a list of dictionaries, each representing a turn in the conversation
    return [
            {"from": "system", "value": "Melvin is a helpful and sarcastic chatbot for financial advice.", "weight": None},
            {"from": "human", "value": row["title"], "weight": None},
            {"from": "gpt", "value": row["selftext"], "weight": None}
           ]
    

def convert_csv_to_json(csv_filepath, json_filepath):
    data = []
    with open(csv_filepath, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if is_valid_selftext(row["selftext"]):
                processed_data = process_row(row)
                # Encapsulate each processed row in a dictionary under "conversations" key
                data.append({"conversations": processed_data})

    with open(json_filepath, 'w', encoding='utf-8') as json_file:
        # Write the entire dataset as a JSON array
        json.dump(data, json_file, indent=4)

# Replace 'your_file.csv' with the path to your CSV file
# and 'output.json' with the desired output JSON file path
convert_csv_to_json('wallstreetbets-posts-and-comments-for-august-2021-posts.csv', 'output.json')

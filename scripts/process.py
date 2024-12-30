import json
import os

def main():
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the path to input.json (one directory up from the script)
    json_path = os.path.join(script_dir, '..', 'input.json')
    
    try:
        # Read the JSON file
        with open(json_path, 'r') as file:
            data = json.load(file)
        
        # Print the content
        print("Contents of input.json:")
        print(json.dumps(data, indent=2))
        
    except FileNotFoundError:
        print(f"Error: The file {json_path} was not found.")
    except json.JSONDecodeError:
        print(f"Error: The file {json_path} is not a valid JSON file.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()

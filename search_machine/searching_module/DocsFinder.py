import re

def open_file(number):
    folder_number = number // 10000  # Calculate folder number
    file_name = f"{number}.txt"  # Construct file name

    file_path = f"/src/search_machine\searching_module\data\collections/{folder_number}/{file_name}"

    try:
        with open(file_path, 'r', encoding="utf-8") as file:
            content = file.read()
        tokenizer_pattern = r'\w+'
        tokens = re.findall(tokenizer_pattern, content)
        return content, tokens
    except FileNotFoundError:
        return '', []
    
def get_content(number):
    folder_number = number // 10000  # Calculate folder number
    file_name = f"{number}.txt"  # Construct file name

    file_path = f"/src/search_machine\searching_module\data\collections/{folder_number}/{file_name}"

    try:
        with open(file_path, 'r', encoding="utf-8") as file:
            content = file.read()
        return content
    except FileNotFoundError:
        return []

if __name__ == "__main__":
    # Example usage
    number = 10132
    content = open_file(number)
    print(content)

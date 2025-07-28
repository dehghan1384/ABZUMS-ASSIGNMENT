import json
import requests

def start_game():
    url="https://mastermind.darkube.app/game"
    response = requests.post(url)
    data = response.json()
    return data["game_id"]
def send_guess(game_id, guess):
    url = "https://mastermind.darkube.app/guess"
    body = {"game_id": game_id, "guess": guess}
    response = requests.post(url, json=body)
    return response.json()

def prompt_guess(game_id):
    while True:
        guess = input("guess 4-digit number (comprises 1 to 6)").strip()
        
        # اعتبارسنجی حدس
        if len(guess) != 4:
            print("number should have four digits")
            continue
        
        if not all('1' <= digit <= '6' for digit in guess):
            print("All digits should be between 1 and 6")
    


        if len(set(guess)) != 4:
            print("repeated digit is not allowed")
            continue

        # ارسال حدس و دریافت پاسخ
        result = send_guess(guess= guess, game_id= game_id)
        
        # نمایش نتیجه
        blacks = result.get("black", '*')
        whites = result.get("white", '*')
        print(f"correct digit value and position BLACK: {blacks}, just correct digit value (wrong position) WHITE: {whites}")

        # اگر بردیم، حلقه را بشکن
        if blacks == 4:
            print("🎉horray")
            break
def run_game():
    print("=== wellcome to Mastermind ===")
    s = start_game()
    print(f"your game id : {s}")
    prompt_guess(s)
    print("=== game has ended===")
if __name__ == "__main__":
    run_game()

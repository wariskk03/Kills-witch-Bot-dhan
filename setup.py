import json
import os
from helper import get_input

CONFIG_PATH = "config_vars.json"

def load_existing_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {"access_token": "", "daily_risk": 0}

def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

def prompt_for_value(label, current_value=None):
    prompt = f"{label}"
    if current_value:
        prompt += f" [{current_value}]"
    prompt += ": "
    value = input(prompt).strip()
    return value or current_value

def setup():
    print("🔧 Kill Switch Bot Setup")
    print("-" * 40)

    config = load_existing_config()

    print(f"\nCurrent config:\n  Access Token: {config['access_token'][:6]}... (hidden)\n  Daily Risk: ₹{config['daily_risk']}")
    
    print("\nWhat would you like to edit?")
    print("1. Access Token")
    print("2. Daily Risk")
    print("3. Both")
    print("4. Cancel")
    
    choice = get_input("Enter your choice (1-4): ", valid_input={"1","2","3","4"}).strip()

    if choice == "1":
        config["access_token"] = prompt_for_value("Enter new access token", config["access_token"])
    elif choice == "2":
        config["daily_risk"] = float(prompt_for_value("Enter new daily risk", config["daily_risk"]))
    elif choice == "3":
        config["access_token"] = prompt_for_value("Enter new access token", config["access_token"])
        config["daily_risk"] = float(prompt_for_value("Enter new daily risk", config["daily_risk"]))
    elif choice == "4":
        print("❌ Setup cancelled.")
        return
 
    save_config(config)
    print(f"\n✅ Config saved to `{CONFIG_PATH}`.")
    print("🚀 You can now run the bot using `python main.py`")

if __name__ == "__main__":
    setup()

    
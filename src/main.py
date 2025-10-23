from utils.integrations import get_env_var
from utils.model_interaction import main as interact


def main():
    pw = get_env_var("ANTHROPIC_API_KEY")
    print(f"Anthropic Api key: {pw[:10]}...")
    print("Running interactions...")
    interact()


if __name__ == "__main__":
    main()

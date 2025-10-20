from utils.integrations import get_env_var
from utils.io_functions import get_ip


def main():
    your_ip = get_ip()
    print(f"Your IP is: {your_ip}")
    pw = get_env_var("ANTHROPIC_API_KEY")
    print(f"Anthropic Api key: {pw[:10]}...")


if __name__ == "__main__":
    main()

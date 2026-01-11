# BOT_CLI_v2.py
from random import random
import random

# Варіанти прощальних повідомлень
GOODBYE_MESSAGES = [
    "Good bye!",
    "See you later!",
    "Take care!",
    "Have a great day!",
    "Bye! Come back anytime.",
    "Session ended. Stay safe.",
    "Until next time!",
    "Good bye! 👋"
]

INVALID_COMMAND_MESSAGE = "Invalid command."

# Повідомлення для послідовних натискань Enter без введення тексту
EMPTY_INPUT_MESSAGES = [
    # 1 — м’яко і весело
    "Hey there 🙂 It looks like you pressed Enter without typing anything.",
    # 2 — весело
    "Still nothing? No worries — keyboards can be shy sometimes 😄",
    # 3 — м’яко, але вже не весело
    "Please type a command when you are ready.",
    # 4 — нейтрально
    "No command detected. Waiting for your input.",
    # 5 — нейтрально з легким сарказмом
    "Pressing Enter without a command usually does not help, you know.",
    # 6 — сарказм
    "At this point, Enter alone is not doing much.",
    # 7 — жарт над користувачем
    "Is Enter your favorite command today? Just curious 🙂",
    # 8 — жарт із сарказмом
    "Enter. Again. Bold strategy.",
    # 9 — серйозний натяк
    "Something seems off. You need to type a command to continue.",
    # 10 — ввічливий вступ перед help
    "It looks like you might need some help. Here are the available commands:"
]


def input_error(func):
    # Декоратор для обробки помилок введення користувача з повідомленнями під конкретну команду
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except IndexError:
            # Немає необхідних аргументів (узагальнене повідомлення)
            return "Enter the argument for the command"

        except ValueError:
            # Невірна кількість аргументів (повідомлення залежить від команди)
            if func.__name__ == "add_contact":
                return "Give me name and phone please."
            if func.__name__ == "change_contact":
                return "Give me name and phone please."
            if func.__name__ == "show_phone":
                return "Enter user name."
            return "Invalid arguments."

        except KeyError:
            # Контакт не знайдено
            return "Contact not found."

    return inner


def parse_input(user_input: str):
    # Парсить введення користувача на команду та аргументи
    user_input = user_input.strip()

    if not user_input:
        return "", []

    parts = user_input.split()
    command = parts[0].lower()
    args = parts[1:]
    return command, args


@input_error
def add_contact(args, contacts: dict) -> str:
    # Додає контакт у словник контактів
    if len(args) != 2:
        raise ValueError

    name, phone = args
    contacts[name] = phone
    return "Contact added."


@input_error
def change_contact(args, contacts: dict) -> str:
    # Змінює номер телефону для існуючого контакту
    if len(args) != 2:
        raise ValueError

    name, new_phone = args
    if name not in contacts:
        raise KeyError

    contacts[name] = new_phone
    return "Contact updated."


@input_error
def show_phone(args, contacts: dict) -> str:
    # Повертає телефон за ім'ям контакту
    if len(args) != 1:
        raise ValueError

    name = args[0]
    if name not in contacts:
        raise KeyError

    return contacts[name]


@input_error
def show_all(contacts: dict) -> str:
    # Повертає всі контакти у відсортованому вигляді
    if not contacts:
        return "No contacts saved."

    lines = []
    for name in sorted(contacts):
        lines.append(f"{name}: {contacts[name]}")
    return "\n".join(lines)


def show_help() -> str:
    # Виводить підказку по доступним командам
    return (
        "\n"
        "================ AVAILABLE COMMANDS ================\n"
        "\n"
        " hello                     → Prints a greeting message\n"
        " add <username> <phone>    → Add a new contact\n"
        " change <username> <phone> → Update an existing contact\n"
        " phone <username>          → Show phone number for contact\n"
        " all                       → Show all saved contacts\n"
        " close | exit              → Exit the assistant bot\n"
        "\n"
        "====================================================\n"
    )

def main() -> None:
    # Головний цикл роботи бота
    contacts = {}
    empty_input_count = 0

    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)

        # Обробка порожнього введення (натискання Enter)
        if command == "":
            index = empty_input_count % len(EMPTY_INPUT_MESSAGES)
            print(EMPTY_INPUT_MESSAGES[index])
            empty_input_count += 1

            # На кожне 10 натискання показуємо help
            if empty_input_count % len(EMPTY_INPUT_MESSAGES) == 0:
                print()
                print(show_help())

            continue

        # Якщо введено будь-яку команду — скидаємо лічильник
        empty_input_count = 0

        if command in ("close", "exit"):
        # Виводимо випадкове прощальне повідомлення
             print(random.choice(GOODBYE_MESSAGES))
             break

        if command == "hello":
            print("How can I help you?")
        elif command == "help":
            print(show_help())
        elif command == "add":
            print(add_contact(args, contacts))
        elif command == "change":
            print(change_contact(args, contacts))
        elif command == "phone":
            print(show_phone(args, contacts))
        elif command == "all":
            print(show_all(contacts))
        else:
            print(INVALID_COMMAND_MESSAGE)


if __name__ == "__main__":
    main()
    
from __future__ import annotations

from typing import Tuple

# =========================
# ТЕКСТОВІ ПОВІДОМЛЕННЯ (UX)
# =========================

AUTO_HELP_EVERY_EMPTY_INPUTS: int = 6

WELCOME_MESSAGES: Tuple[str, ...] = (
    "👋🙂 Welcome to the assistant bot!\nThis tool helps you manage your contacts.\nType 'help' to see commands. =)",
    "🤖✨ Welcome!\nContact management is ready.\nEnter 'help' to see all commands ->",
    "👋😊 Hello and welcome!\nAdd, update, search and manage contacts.\nUse 'help' to get started. =)",
    "📇🙂 Welcome!\nYour contact assistant is online.\nType 'help' for guidance ->",
    "👋🤝 Hi there!\nLet’s keep your contacts tidy.\nType 'help' to begin. =)",
    "🤖🙂 Welcome!\nQuick contact management starts here.\nUse 'help' anytime ->",
    "✨👋 Welcome!\nI can help you add/find/update contacts.\nType 'help' to see options. =)",
    "🙂📞 Welcome!\nYour address book assistant is ready.\nType 'help' to learn commands ->",
    "👋🧭 Welcome!\nNot sure where to start?\nType 'help' and pick a command. =)",
    "🤖📌 Welcome!\nSimple CLI. Serious usefulness.\nType 'help' for the menu ->",
)

GOODBYE_MESSAGES: Tuple[str, ...] = (
    "👋🙂 Good bye! Thanks for using the assistant bot. =)",
    "😊👋 Good bye! See you next time! =)",
    "🌤️🙂 Good bye! Have a great day! =)",
    "🔒✅ Session ended. Your contacts are safe. =)",
    "💾🙂 Saved! Good bye and take care! =)",
    "🤝👋 Thanks for choosing the assistant bot! =)",
    "✨🙂 Bye! Stay productive and calm. =)",
    "🚀👋 Good bye! Come back anytime. =)",
    "😄👋 See you later! =)",
    "📇🙂 Address book closed. Bye! =)",
)

HELP_MESSAGE: str = (
    "┌──────────────────────────────────────────────────────────────┐\n"
    "│                   🤖  ASSISTANT BOT — HELP  🤖               │\n"
    "├──────────────────────────────────────────────────────────────┤\n"
    "│ 📌 BASIC COMMANDS                                            │\n"
    "├──────────────────────────────┬───────────────────────────────┤\n"
    "│ hello                        │ Print a greeting message 👋🙂  │\n"
    "│ help                         │ Show this help screen ℹ️🙂     │\n"
    "├──────────────────────────────┴───────────────────────────────┤\n"
    "│ 📇 CONTACT MANAGEMENT                                        │\n"
    "├──────────────────────────────┬───────────────────────────────┤\n"
    "│ add <name> <phone>           │ Add a new contact ➕🙂          │\n"
    "│ change <name> <phone>        │ Update contact phone ✏️🙂       │\n"
    "│ phone <name>                 │ Show phone by name 📞🙂        │\n"
    "│ all                          │ Show all contacts 📋🙂         │\n"
    "│ remove <name>                │ Remove contact (confirm) 🗑️🙂  │\n"
    "│ delete <name>                │ Same as remove 🗑️🙂            │\n"
    "│ search <query>               │ Search by name/phone 🔎🙂      │\n"
    "│ rename <old> <new>           │ Rename contact ✍️🙂            │\n"
    "│ stats                        │ Show address book stats 📊🙂   │\n"
    "├──────────────────────────────┴───────────────────────────────┤\n"
    "│ 🚪 EXIT                                                      │\n"
    "├──────────────────────────────┬───────────────────────────────┤\n"
    "│ close | exit                 │ Exit the assistant bot 👋🙂     │\n"
    "└──────────────────────────────┴───────────────────────────────┘"
)

EMPTY_INPUT_MESSAGES: Tuple[str, ...] = (
    "⏎🙂 Empty input.\nPlease type a command or use 'help'. =)",
    "🤔🙂 Nothing entered.\nTry a command or type 'help'. ->",
    "📝🙂 No command detected.\nType 'help' to see options. =)",
    "⌨️🙂 Just Enter?\nPlease enter a command (or 'help'). ->",
    "💡🙂 Tip: type 'help' anytime.\nEnter a command to proceed. =)",
    "👀🙂 I’m still here.\nPlease type a command. ->",
    "🧭🙂 Not sure what to do?\nType 'help' and pick a command. =)",
    "📌🙂 Waiting for your input...\nType a command or 'help'. ->",
    "🕒🙂 Still waiting...\nType something meaningful. =)",
    "✨🙂 Start with 'help'.\nIt’s the safest move. ->",
)

INVALID_COMMAND_MESSAGES: Tuple[str, ...] = (
    "❌🙂 Invalid command.\nType 'help' to see supported commands. ->",
    "🚫🙂 Command not recognized.\nUse 'help' for the list. =)",
    "📛🙂 Unsupported command.\nType 'help' to view options. ->",
    "🤔🙂 Unknown command.\nCheck spelling or type 'help'. =)",
    "📘🙂 Need help?\nType 'help' to continue. ->",
    "⚠️🙂 I can’t do that.\nTry 'help' for available commands. =)",
    "🔎🙂 Not found.\nType 'help' to see the menu. ->",
    "🧠🙂 I didn’t understand.\nUse 'help' and try again. =)",
    "🧭🙂 Wrong direction.\nType 'help' for guidance. ->",
    "🙃🙂 Nope.\nType 'help' and we’ll pretend it never happened. =)",
)

NO_CONTACTS_MESSAGES: Tuple[str, ...] = (
    "📭🙂 No contacts saved yet.\nUse 'add' to create one. =)",
    "📂🙂 Your contact list is empty.\nStart with 'add <name> <phone>'. ->",
    "🗒️🙂 No contacts found.\nTry adding your first contact. =)",
    "✨🙂 Nothing here yet.\nUse 'add' to begin. ->",
    "📘🙂 Empty address book.\nType 'add' to create a contact. =)",
    "📞🙂 No contacts.\nAdd one and we’ll talk again. ->",
    "🧭🙂 Start simple:\nadd John +123456789. =)",
    "🚀🙂 Ready when you are.\nAdd your first contact. ->",
    "🙂📇 No entries.\nUse 'add' to populate the list. =)",
    "💡🙂 Tip:\nUse 'help' if you forget syntax. ->",
)

CONTACT_ADDED_MESSAGES: Tuple[str, ...] = (
    "✅🙂 Contact added successfully. =)",
    "📇🙂 Contact saved. ->",
    "💾🙂 Stored successfully. =)",
    "➕🙂 Added to address book. ->",
    "🎉🙂 Done! Contact created. =)",
    "👍🙂 Added. Nice and clean. ->",
    "✨🙂 Saved without issues. =)",
    "🤝🙂 Contact added. ->",
    "📌🙂 New contact stored. =)",
    "✅🙂 Added and ready to use. ->",
)

CONTACT_UPDATED_MESSAGES: Tuple[str, ...] = (
    "✏️🙂 Contact updated successfully. =)",
    "🔄🙂 Updated. ->",
    "💾🙂 Changes saved. =)",
    "📝🙂 Contact details updated. ->",
    "✅🙂 Update complete. =)",
    "📇🙂 Contact refreshed. ->",
    "🔧🙂 Updated successfully. =)",
    "👍🙂 Done. Contact updated. ->",
    "✨🙂 Updated cleanly. =)",
    "✅🙂 Saved changes. ->",
)

DUPLICATE_NAME_MESSAGES: Tuple[str, ...] = (
    "⚠️🙂 A contact with this name already exists.\nUse 'change <name> <phone>' or 'rename'. ->",
    "📛🙂 This name is already taken.\nChoose a different name or use 'rename'. =)",
    "🔁🙂 Duplicate name detected.\nTry another name or update the existing contact. ->",
    "🤔🙂 Name already exists.\nUse 'change' to update phone. =)",
    "📇🙂 That contact name is already registered.\nUse 'rename' if needed. ->",
    "⚠️🙂 Duplicate detected.\nNo overwrite without your permission. =)",
    "🧭🙂 Name conflict.\nTry 'rename old new'. ->",
    "📘🙂 Existing name.\nUse 'change' or 'rename'. =)",
    "🔍🙂 Name already in the book.\nPick a new one. ->",
    "🙃🙂 That name is famous already.\nTry a different one. =)",
)

DUPLICATE_PHONE_MESSAGES: Tuple[str, ...] = (
    "📞🙂 This phone number is already in use.\nProvide a different one. ->",
    "🚫🙂 Duplicate phone detected.\nPhone numbers must be unique. =)",
    "🔒🙂 This number belongs to another contact.\nTry another number. ->",
    "⚠️🙂 Duplicate phone number.\nUse a different value. =)",
    "📘🙂 Phone already exists.\nPlease provide a new phone. ->",
    "🧭🙂 Number conflict.\nPick another one. =)",
    "🔍🙂 This phone is already assigned.\nUse a different one. ->",
    "🤔🙂 Same phone found.\nWe keep phones unique here. =)",
    "📇🙂 Phone already registered.\nTry another. ->",
    "🙃🙂 This number is taken.\nTry a new one. =)",
)

ENTER_NAME_MESSAGES: Tuple[str, ...] = (
    "🙂 Please enter a contact name. =)",
    "👋🙂 Enter user name, please. ->",
    "📝🙂 Name is required. =)",
    "📌🙂 Please provide a name. ->",
    "🤔🙂 Missing name.\nType a name. =)",
    "🧭🙂 You need a name for this command. ->",
    "📇🙂 Contact name is missing. =)",
    "⌨️🙂 Type the name first. ->",
    "⚠️🙂 Name cannot be empty. =)",
    "🙂 Provide the contact name, please. ->",
)

ENTER_NAME_AND_PHONE_MESSAGES: Tuple[str, ...] = (
    "🙂 Give me name and phone please. =)",
    "📌🙂 Please provide name and phone. ->",
    "📝🙂 Two arguments required: name and phone. =)",
    "🤔🙂 Missing name and phone.\nExample: add Bob +123. ->",
    "⌨️🙂 Enter name and phone, please. =)",
    "📇🙂 Name and phone are required here. ->",
    "⚠️🙂 Provide both values: <name> <phone>. =)",
    "🙂 Example:\nadd John +353871234567 ->",
    "📘🙂 Please enter: name phone. =)",
    "🧭🙂 I need two values: name + phone. ->",
)

ENTER_COMMAND_ARGUMENTS_MESSAGES: Tuple[str, ...] = (
    "🙂 Enter the argument for the command. =)",
    "📌🙂 Please enter command arguments. ->",
    "📝🙂 Arguments are missing. =)",
    "🤔🙂 This command needs more info. ->",
    "⌨️🙂 Provide required arguments, please. =)",
    "📘🙂 Missing parameters.\nType 'help' for syntax. ->",
    "⚠️🙂 Not enough arguments. =)",
    "🙂 Add arguments and try again. ->",
    "🧭🙂 This command requires extra input. =)",
    "📌🙂 Please provide the required values. ->",
)

REMOVE_CONFIRM_MESSAGES: Tuple[str, ...] = (
    "🗑️🙂 Type YES to confirm deletion: ",
    "⚠️🙂 Confirm removal. Type YES: ",
    "🧹🙂 Are you sure? Type YES to proceed: ",
)

REMOVE_CANCELED_MESSAGES: Tuple[str, ...] = (
    "🙂 Deletion canceled. =)",
    "✅🙂 Nothing deleted. =)",
    "🧘🙂 Okay, keeping the contact. =)",
)

CONTACT_REMOVED_MESSAGES: Tuple[str, ...] = (
    "🗑️🙂 Contact removed successfully. =)",
    "✅🙂 Deleted. =)",
    "🧹🙂 Removed from address book. =)",
)
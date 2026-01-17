# ux_messages.py
"""UX-повідомлення (константи) для бота.

Увага:
- Тут лише текст/налаштування, без логіки.
- Файл зручно згортати у редакторі (або винести в окремий модуль — вже зроблено).
"""

from __future__ import annotations

from typing import Tuple

# Політики
ALLOW_DUPLICATE_PHONES: bool = False
AUTO_HELP_EVERY_EMPTY_INPUTS: int = 6

WELCOME_MESSAGES: Tuple[str, ...] = (
    "👋🙂 Welcome to the assistant bot.\nThis tool helps you manage contacts efficiently.\nType 'help' to see commands. =)",
    "🤖✨ Welcome!\nConsole contact assistant is ready.\nEnter 'help' to view commands. ->",
    "👋😄 Hello!\nAdd, update, search, and manage contacts here.\nUse 'help' to get started. =)",
    "📇🙂 Welcome!\nKeep your contact list clean and organized.\nType 'help' for guidance. ->",
    "😊🤝 Welcome aboard!\nI can help you store and update contacts.\nType 'help' anytime. =)",
    "🚀🙂 Welcome!\nFast contact management starts here.\nType 'help' to begin. ->",
    "👋✨ Hi there!\nI’m ready to manage your address book.\nUse 'help' for options. =)",
    "🤖🙂 Welcome!\nYour contacts deserve order.\nType 'help' to see what I can do. ->",
    "📞🙂 Welcome!\nLet’s keep your contacts accessible.\nType 'help' to start. =)",
    "🌟🙂 Welcome!\nSimple commands, clean results.\nType 'help' to explore. ->",
)

GOODBYE_MESSAGES: Tuple[str, ...] = (
    "👋😊 Good bye! Thanks for using the assistant bot. =)",
    "🌤️🙂 See you next time! Have a great day. ->",
    "🔒🙂 Session ended. Your contacts are safe. =)",
    "💾🙂 All changes saved. Good bye! ->",
    "🤝😊 Thanks for choosing the assistant bot. Take care! =)",
    "✨👋 Bye bye! Until next time. ->",
    "🚀🙂 Goodbye! Come back anytime you need help. =)",
    "📇🙂 Session closed successfully. Bye! ->",
    "😄👋 See you later! Have a nice day. =)",
    "✅🙂 Done for now. Good bye! ->",
)

HELP_MESSAGE: str = (
    "┌──────────────────────────────────────────────────────────────┐\n"
    "│                   🤖  ASSISTANT BOT — HELP  🤖               │\n"
    "├──────────────────────────────────────────────────────────────┤\n"
    "│ 📌 BASIC COMMANDS                                            │\n"
    "├──────────────────────────────┬───────────────────────────────┤\n"
    "│ hello                        │ Print a greeting message 👋🙂 │\n"
    "│ help                         │ Show this help screen ℹ️🙂    │\n"
    "├──────────────────────────────┴───────────────────────────────┤\n"
    "│ 📇 CONTACT MANAGEMENT                                        │\n"
    "├──────────────────────────────┬───────────────────────────────┤\n"
    "│ add <name> <phone>           │ Add a new contact ➕📇        │\n"
    "│ change <name> <phone>        │ Update phone number ✏️📞      │\n"
    "│ phone <name>                 │ Show phone for contact 📞🙂   │\n"
    "│ all                          │ Show all contacts 📋🙂        │\n"
    "│ search <query>               │ Search by name/phone 🔎🙂     │\n"
    "│ rename <old> <new>           │ Rename contact 🏷️🙂           │\n"
    "│ remove <name> | delete <name>│ Remove contact 🗑️⚠️           │\n"
    "│ stats                        │ Show stats 📊🙂               │\n"
    "├──────────────────────────────┴───────────────────────────────┤\n"
    "│ 🚪 EXIT                                                      │\n"
    "├──────────────────────────────┬───────────────────────────────┤\n"
    "│ close | exit                 │ Exit the assistant bot 👋🙂   │\n"
    "└──────────────────────────────┴───────────────────────────────┘"
)

INVALID_COMMAND_MESSAGES: Tuple[str, ...] = (
    "❌🙂 Invalid command.\nType 'help' to see supported commands. ->",
    "🚫🙂 Command not recognized.\nUse 'help' for guidance. =)",
    "📛🙂 This command is not supported.\nType 'help' to view options. ->",
    "🤔🙂 Unknown command.\nCheck spelling or type 'help'. =)",
    "📘🙂 Need help?\nType 'help' to continue. ->",
    "🔎🙂 I can’t find that command.\nTry 'help'. =)",
    "⚠️🙂 Not a valid command.\nType 'help' to see the list. ->",
    "🙃🙂 That doesn’t look right.\nUse 'help' for commands. =)",
    "🧭🙂 Not sure what you meant.\nType 'help'. ->",
    "✅🙂 Tip: use 'help' to explore commands. =)",
)

NO_CONTACTS_MESSAGES: Tuple[str, ...] = (
    "📭🙂 No contacts saved yet.\nUse 'add' to create one. ->",
    "📂🙂 Your contact list is empty.\nStart by adding a contact. =)",
    "🗒️🙂 No contacts found.\nTry: add John +123456789 ->",
    "🚀🙂 Let’s begin!\nAdd your first contact. =)",
    "💡🙂 Tip: 'add John +123456789'\ncreates a contact. ->",
    "📞🙂 No contacts available.\nAdd one to get started. =)",
    "✨🙂 Empty list.\nUse 'add' to fill it. ->",
    "📘🙂 Nothing saved yet.\nType 'add' to create a contact. =)",
    "🧭🙂 Your book is empty.\nAdd contacts to proceed. ->",
    "🤝🙂 Ready?\nAdd your first contact now. =)",
)

CONTACT_ADDED_MESSAGES: Tuple[str, ...] = (
    "✅🙂 Contact added successfully! 📇👍",
    "📇🙂 Contact has been saved. ✅💾",
    "💾🙂 New contact stored. ✅📞",
    "🎉🙂 Contact added! You’re all set. ✅✨",
    "➕🙂 Contact added to your list. ✅📋",
    "👍🙂 Successfully added the contact. ✅📇",
    "✨🙂 Contact saved without issues. ✅🙂",
    "📞🙂 Contact registered successfully. ✅📇",
    "🤝🙂 Contact added. Nice work! ✅🙂",
    "🗂️🙂 Contact added to your address book. ✅📇",
)

CONTACT_UPDATED_MESSAGES: Tuple[str, ...] = (
    "✏️🙂 Contact updated successfully. ✅📞",
    "🔄🙂 Contact information updated. ✅💾",
    "💾🙂 Changes saved. ✅🙂",
    "📝🙂 Contact details updated. ✅📇",
    "✅🙂 Update completed. 📞✨",
    "📇🙂 Contact updated in your list. ✅📋",
    "✨🙂 Contact refreshed. ✅🙂",
    "👍🙂 Update successful. ✅📞",
    "📞🙂 Phone updated. ✅🙂",
    "🔧🙂 Contact modified successfully. ✅📇",
)

ENTER_NAME_MESSAGES: Tuple[str, ...] = (
    "🙂👤 Please enter a contact name. =)",
    "👋🙂 Enter user name, please. ->",
    "📝🙂 Name is required to continue. =)",
    "🤝🙂 Please provide a name. ->",
    "⚠️🙂 Contact name is missing. =)",
    "⌨️🙂 Type a name to proceed. ->",
    "📇🙂 A name is required here. =)",
    "🔎🙂 Please specify the contact name. ->",
    "🙂🧭 Enter the name first. =)",
    "✅🙂 Name cannot be empty. ->",
)

ENTER_NAME_AND_PHONE_MESSAGES: Tuple[str, ...] = (
    "🙂📞 Please provide both name and phone number. =)",
    "👋🙂 Give me name and phone, please. ->",
    "📝🙂 Name and phone are required. =)",
    "⌨️🙂 Enter name and phone number. ->",
    "⚠️🙂 Both name and phone must be specified. =)",
    "🙂📘 Missing arguments: name and phone. ->",
    "📇🙂 Please enter contact name and phone. =)",
    "🤝🙂 You need to provide name and phone. ->",
    "✅🙂 Two arguments required: name and phone. =)",
    "🙂🧭 Contact name and phone are missing. ->",
)

ENTER_COMMAND_ARGUMENTS_MESSAGES: Tuple[str, ...] = (
    "🙂📝 Please provide command arguments. =)",
    "👋🙂 This command needs additional input. ->",
    "⚠️🙂 Arguments are missing for this command. =)",
    "⌨️🙂 Enter the required arguments. ->",
    "🙂📘 Command arguments expected. =)",
    "🧭🙂 Please add arguments to the command. ->",
    "🙂🔎 Missing command parameters. =)",
    "📌🙂 This command needs more information. ->",
    "🙂✅ Provide arguments to continue. =)",
    "📋🙂 Arguments required to proceed. ->",
)

CONFIRM_REMOVE_MESSAGES: Tuple[str, ...] = (
    "⚠️🗑️ You are about to remove '{name}'.\nType YES to confirm. 🙂",
    "🗑️⚠️ Confirm deletion of '{name}'.\nType YES to proceed. 🙂",
    "⚠️🙂 Remove '{name}'?\nType YES to confirm. 🗑️",
    "🧭⚠️ This will delete '{name}'.\nType YES to confirm. 🗑️",
    "🙂⚠️ Please confirm removal of '{name}'.\nType YES. 🗑️",
)

OPERATION_CANCELLED_MESSAGES: Tuple[str, ...] = (
    "🙂✅ Cancelled. No changes were made. =)",
    "🙃🙂 Operation cancelled. Nothing deleted. ->",
    "✅🙂 Okay, I won’t remove anything. =)",
    "🙂📌 Cancelled. Your contacts remain unchanged. ->",
    "🤝🙂 Cancelled. All good. =)",
)

REMOVE_SUCCESS_MESSAGES: Tuple[str, ...] = (
    "🗑️🙂 Contact removed successfully. ✅📇",
    "✅🙂 Deleted. Contact is gone. 🗑️",
    "🧹🙂 Contact removed. ✅🗑️",
    "📇🙂 Contact deleted successfully. ✅🗑️",
    "✅🙂 Removal completed. 🗑️🙂",
)

RENAME_SUCCESS_MESSAGES: Tuple[str, ...] = (
    "🏷️🙂 Contact renamed successfully. ✅📇",
    "✅🙂 Rename completed. 🏷️🙂",
    "📇🙂 Name updated successfully. ✅🏷️",
    "🏷️✅ Contact name changed. 🙂📇",
    "🙂🏷️ Renamed. All set. ✅📇",
)

SEARCH_NO_RESULTS_MESSAGES: Tuple[str, ...] = (
    "🔎🙂 No matches found. Try a different query. =)",
    "🙃🔎 Nothing found. Please refine your search. ->",
    "🔍🙂 No results. Check spelling or try another value. =)",
    "🙂📘 No contacts matched your query. ->",
    "🔎🙂 Empty result. Try searching by phone digits. =)",
)

STATS_HEADER_MESSAGES: Tuple[str, ...] = (
    "📊🙂 Address book stats: =)",
    "🙂📈 Stats overview: ->",
    "📊✅ Current statistics: 🙂",
    "🙂📊 Here are your stats: =)",
    "📈🙂 Summary: ->",
)
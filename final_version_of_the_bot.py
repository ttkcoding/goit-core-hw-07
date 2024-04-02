from collections import UserDict
from datetime import datetime, timedelta

# Base class for different types of fields in a record
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
    
# Class for storing a contact's name
class Name(Field):
    pass

# Class for storing a contact's phone number
class Phone(Field):
    def __init__(self, value):
        if isinstance(value, str) and value.isdigit() and len(value) == 10:
            super().__init__(value)
        else:
            raise ValueError("Number is too short")
        
# Class for storing a contact's birthday
class Birthday(Field):
    def __init__(self, value):
        try:
            self.date = datetime.strptime(value, "%d.%m.%Y")
            self.value = value
        except ValueError:
            raise ValueError(f"Value '{value}' is not a valid date in the format DD.MM.YYYY")
        
# Class for record a contact's information
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_birthday(self, date):
        if isinstance(date, Birthday):
            self.birthday = date
        else:
            raise ValueError("Date must be an instance of Birthday class")


    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            if phone.value == old_phone:
                phone.value = new_phone
    
    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None
            
    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"
    
# Class for storing a collection of contacts
class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)
    
    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def get_upcoming_birthdays(self):
        congratulation_list = []
        current_date = datetime.today().date()
        for name, record in self.data.items():
            if record.birthday:
                birthday = record.birthday.date
                birthday_this_year = birthday.replace(year=current_date.year).date()
                if birthday_this_year < current_date:
                    birthday_this_year = birthday_this_year.replace(year=current_date.year + 1)
                days_to_birthday = (birthday_this_year - current_date).days
                if 0 <= days_to_birthday < 8:
                    if birthday_this_year.weekday() >= 5:
                        days_to_birthday += (7 - birthday_this_year.weekday())
                    congratulation_date = current_date + timedelta(days=days_to_birthday)
                    congratulation_list.append({"name": name, "congratulation_date": congratulation_date})
        return congratulation_list

# Decorator for handling errors in command functions
def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except IndexError:
            return "Enter contact Name please."
        except KeyError:
            return "Contact not found"

    return inner

# Command function to add a new contact
@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args
    record = book.find(name)
    message = "Contact updated."

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."

    if phone:
        record.add_phone(phone)

    return message

# Command function to change a contact's phone number
@input_error
def change_contact(args, book: AddressBook):
    name, new_phone, *_ = args
    record = book.find(name)
    if record is None:
        raise KeyError

    if not record.phones:
        raise ValueError

    old_phone = record.phones[0].value
    if old_phone != new_phone:
        record.edit_phone(old_phone, new_phone)
        message = "Contact updated."
    else:
        message = "Phone number is already up to date."

    return message

# Command function to show a contact's phone number
@input_error
def show_contact(args, book: AddressBook):
    if len(args) != 1:
        raise IndexError
    name = args[0]
    record = book.find(name)

    if record:
        return str(record)
    else: 
        raise KeyError

# Command function to show all contacts    
def show_all_contacts(book: AddressBook):
    if not book.data:
        return "No contacts found"
    all_contacts = [str(record) for record in book.data.values()]
    return "\n\n".join(all_contacts)

# Command function to add a birthday to a contact
@input_error
def add_birthday(args, book: AddressBook):
    name, birthday_str, *_ = args
    record = book.find(name)
    message = "Contact updated."

    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    try:
        birthday = Birthday(birthday_str)
        record.add_birthday(birthday)
    except ValueError as e:
        raise ValueError(f"Error adding birthday: {e}")
    
    return message

# Command function to show a contact's birthday
@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]
    record = book.find(name)

    if record is None:
        raise KeyError

    if record.birthday:
        return f"{name}'s birthday is on {record.birthday.value}"
    else:
        return f"No birthday information for {name}."

# Command function to show birthdays in the next week  
def next_week_birthday(book: AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if upcoming_birthdays:
        return "\n".join([f"{item['name']}'s birthday is on {item['congratulation_date'].strftime('%d.%m.%Y')}" for item in upcoming_birthdays])
    else:
        return "No birthdays in the next week."

# Function to parse user input into command and arguments
def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

# Main loop of the program
def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_contact(args, book))

        elif command == "all":
            print(show_all_contacts(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(next_week_birthday(book))    

        else:
            print("Invalid command.")



if __name__ == "__main__":
    main()
from collections import UserDict
from datetime import datetime, timedelta


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)
    

class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        if isinstance(value, str) and value.isdigit() and len(value) == 10:
            super().__init__(value)
        else:
            raise ValueError("Number is too short")
        

class Birthday(Field):
    def __init__(self, value):
        try:
            self.date = datetime.strptime(value, "%d.%m.%Y")
            self.value = value
        except ValueError:
            raise ValueError(f"Value '{value}' is not a valid date in the format DD.MM.YYYY")
        

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
                birthday_this_year = birthday.replace(year=current_date.year)
                if birthday_this_year < current_date:
                    birthday_this_year = birthday_this_year.replace(year=current_date.year + 1)
                days_to_birthday = (birthday_this_year - current_date).days
                if 0 <= days_to_birthday < 8:
                    if birthday_this_year.weekday() >= 5:
                        days_to_birthday += (7 - birthday_this_year.weekday())
                    congratulation_date = current_date + timedelta(days=days_to_birthday)
                    congratulation_list.append({"name": name, "congratulation_date": congratulation_date})
        return congratulation_list
    

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

def show_contact(args, book: AddressBook):
    if len(args) != 1:
        raise IndexError
    name = args[0]
    record = book.find(name)
    if record:
        return str(record)
    else: 
        raise KeyError
    
def show_all_contacts(book: AddressBook):
    all_contacts = [str(record) for record in book.data.values()]
    return "\n".join(all_contacts)
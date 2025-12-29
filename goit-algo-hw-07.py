from collections import UserDict
from datetime import datetime
from date_utils import adjust_for_weekend

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
		pass

class Phone(Field):
    def __init__(self, value: str):
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain exactly 10 digits")
        super().__init__(value)
        

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.birthday = None
    
    def add_phone(self, phone: str):
           self.phones.append(Phone(phone))
    
    def remove_phone(self, phone: str):
           phone_obj = self.find_phone(phone)
           self.phones.remove(phone_obj)

    def edit_phone(self, old_phone: str, new_phone: str):
           phone_obj = self.find_phone(old_phone)
           if phone_obj is None:
            raise ValueError("Old phone is not exist")
           phone_obj.value = Phone(new_phone).value
    
    def find_phone(self, phone: str):
        for p in self.phones:
                if p.value == phone:
                    return p
        return None
    
    def add_birthday(self, birthday: str):
         self.birthday = Birthday(birthday)
         

        

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"

class AddressBook(UserDict):

    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str):
        return self.data.get(name)
    
    def delete(self, name):
        del self.data[name]

    def get_upcoming_birthdays(self, days=7):
        today = date.today()
        result = []

        for record in self.data.values():
            if record.birthday is None:
                continue

            birthday_this_year = record.birthday.value.replace(year=today.year)
            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            congratulation_date = adjust_for_weekend(birthday_this_year)

            if 0 <= (congratulation_date - today).days <= days:
                result.append({
                    "name": record.name.value,
                    "congratulation_date": congratulation_date.strftime("%d.%m.%Y") #can't make this key as "birthday", because "birthday" is already exists in adjust_for_weekend(birthday):
                })

        return result
 

class Birthday(Field):
    def __init__(self, value):
        try:
            date = datetime.strptime(value, "%d.%m.%Y").date()
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(date)

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Provide name and phone number."
        except IndexError:
            return "Provide name to show the phone."
        except KeyError:
            return "Name is not found."
    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


@input_error
def add_birthday(args, book: AddressBook):
    name, birthday, *_ = args

    record = book.find(name)
    if record is None:
        raise KeyError
    
    record.add_birthday(birthday)
    return "Birthday added."    

@input_error
def show_birthday(args, book: AddressBook):
    name, *_ = args

    record = book.find(name)
    if record is None:
        raise KeyError

    if record.birthday is None:
        return "Birthday not set."

    return record.birthday.value.strftime("%d.%m.%Y")  

@input_error
def birthdays(args, book: AddressBook):
    upcoming = book.get_upcoming_birthdays()

    if not upcoming:
        return "No birthdays in the next week."

    result = []
    for item in upcoming:
        result.append(
            f"{item['name']}: {item['congratulation_date']}"
        )

    return "\n".join(result)  

    
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

@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone, *_ = args

    record = book.find(name)
    if record is None:
        raise KeyError

    record.edit_phone(old_phone, new_phone)
    return "Phone number updated."


def show_phone(args, book: AddressBook):
    name, *_ = args

    record = book.find(name)
    if record is None:
        raise KeyError

    if not record.phones:
        return "No phone numbers."

    return "; ".join(phone.value for phone in record.phones)

def show_all_contacts(args, book):
    if not book.data:
        return "Address book is empty."

    result = []
    for record in book.data.values():
        phones = "; ".join(p.value for p in record.phones)
        birthday = (
            record.birthday.value.strftime("%d.%m.%Y")
            if record.birthday else "N/A"
        )
        result.append(
            f"Name: {record.name.value}, Phones: {phones}, Birthday: {birthday}"
        )

    return "\n".join(result)


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
            print(show_phone(args, book))

        elif command == "all":
            print(show_all_contacts(args, book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(args, book))

        else:
            print("Invalid command.")


main()





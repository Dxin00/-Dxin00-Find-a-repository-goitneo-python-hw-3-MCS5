from collections import UserDict
from datetime import datetime, timedelta


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Incorrect input format."
        except KeyError:
            return "Contact not found."
        except IndexError:
            return "Please provide a contact name."

    return inner


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, number):
        if self.validate_number(number):
            self.number = number
        else:
            raise ValueError(
                "Invalid phone number format. Please enter a 10-digit number."
            )

    def validate_number(self, number):
        if len(number) == 10 and number.isdigit():
            return True
        else:
            return False

    def __str__(self):
        return str(self.number)


class Birthday(Field):
    def __init__(self, value):
        datetime.strptime(value, "%d.%m.%Y")
        super().__init__(value)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone: str):
        self.phones.append(Phone(phone))

    def edit_phone(self, old_phone: str, new_phone: str):
        for phone in self.phones:
            if phone.number == old_phone:
                phone.number = new_phone
                return "Phone edited."
        return "Phone not found."

    def find_phone(self, phone: str):
        for p in self.phones:
            if p.number == phone:
                return p
        return "Phone not found."

    def add_birthday(self, birthday: str):
        self.birthday = Birthday(birthday)
        return "Birthday added."

    def remove_phone(self, phone: str):
        record_phone = self.find_phone(phone)
        if isinstance(record_phone, Phone):
            self.phones.remove(record_phone)
            return "Phone removed."
        return "Phone not found."

    def __str__(self):
        phone_numbers = ", ".join(p.number for p in self.phones)
        result = f"Contact name: {self.name.value}, phones: {phone_numbers}"
        if self.birthday:
            result += f", birthday: {self.birthday.value}"
        return result


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str):
        return self.data[name]

    def delete(self, name: str):
        del self.data[name]

    def get_records_list(self):
        return list(self.data.values())

    def get_birthdays_per_week(self):
        today = datetime.now()
        next_week = today + timedelta(days=(7 - today.weekday() + 1) % 7)
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y")
                if today <= birthday_date < next_week:
                    upcoming_birthdays.append(record)
        return upcoming_birthdays

    def birthdays(self):
        users_list = self.get_records_list()
        upcoming_birthdays_str = birth_week(users_list)
        result_string = ""

        for record in self.get_birthdays_per_week():
            result_string += (
                f"{record.name.value}'s birthday on {record.birthday.value}\n"
            )

        result_string += (
            f"\nUpcoming birthdays for the next week:\n{upcoming_birthdays_str}"
        )
        return result_string


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


def birth_week(users):
    today = datetime.today().date()
    birth_per_day = {
        "Monday": [],
        "Tuesday": [],
        "Wednesday": [],
        "Thursday": [],
        "Friday": [],
    }

    for record in users:
        name = record.name.value
        if record.birthday:
            birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y").date()
            birth_this_year = birthday_date.replace(year=today.year)

            if birth_this_year < today:
                birth_this_year = birth_this_year.replace(year=today.year + 1)
            delta_days = (birth_this_year - today).days

            if delta_days < 7:
                day_of_week = birth_this_year.strftime("%A")
                if day_of_week in ("Saturday", "Sunday"):
                    birth_per_day["Monday"].append(name)
                else:
                    birth_per_day[day_of_week].append(name)

    result_string = ""
    for day, names in birth_per_day.items():
        if names:
            result_string += f"{day}: {', '.join(names)}\n"
    return result_string


@input_error
def add_contact(args, book):
    if len(args) < 2:
        raise ValueError ("Incorrect input format.")
    name, phone = args
    if len(phone) != 10 or not phone.isdigit():
        print("Incorrect phone format.")
        return None
    else:
        try:
            record = Record(name)
            record.add_phone(phone)
            book.add_record(record)
            return "Contact added successfully."
        except ValueError:
            print("Incorrect phone format.")
            return None


def show_all(book):
    if not book.data:
        return "AddressBook is empty"
    result_string = ""
    for record in book.data.values():
        result_string += str(record) + "\n"
    return result_string


@input_error
def show_phone(args, book):
    name = args[0]
    record = book.find(name)
    return record.find_phone(record.phones[0].number)


@input_error
def change_contact(args, book):
    if len(args) < 2:
        return "Incorrect input format. Please provide both the contact name and the new phone number."
    name, phone = args
    if not phone.isdigit() or len(phone) != 10:
        return "Incorrect phone format."

    record = book.find(name)
    record.edit_phone(record.phones[0].number, phone)
    return "Contact changed."


def add_birthday(args, book):
    if len(args) < 2:
        return 'Incorrect input format. Please enter "command" "name" "dd.mm.yy".'
    else:
        name, birthday = args
        try:
            record = book.find(name)
            result = record.add_birthday(birthday)
            if result:
                return result
        except ValueError as e:
            print(e)


@input_error
def show_birthday(args, book):
    name = args[0]
    record = book.find(name)
    return record.birthday.value


def birthdays(book):
    upcoming_birthdays = book.get_birthdays_per_week()
    users_list = book.get_records_list()
    upcoming_birthdays_str = birth_week(users_list)
    result_string = ""

    for record in upcoming_birthdays:
        result_string += f"{record.name.value}'s birthday on {record.birthday.value}\n"

    result_string += (
        f"\nUpcoming birthdays for the next week:\n{upcoming_birthdays_str}"
    )
    return result_string


def main():
    book = AddressBook()
    print(
        """Welcome to the assistant bot!
Use the following commands to interact with the bot:

"hello"                        - Greeting      
"add"                          - Add contact
"add-birthday"                 - Add date of birth
"change"                       - Change contact number
"all"                          - Show all contact numbers
"phone"                        - Show contact phone number
"show-birthday"                - Show contact's date of birth
"birthdays"                    - Show all dates of birth for the next week
"close" or "exit"              - Exit       

Adding or changing data must be entered in the following order: add [name] [data]
Enjoy your use!
"""
    )
    while True:
        user_input = input("Enter a command: ")
        if user_input.strip():
            command, *args = parse_input(user_input)

            if command in ["close", "exit"]:
                print("Good bye!")
                break
            elif command == "hello":
                print("How can I help you?")
            elif command == "add":
                result = add_contact(args, book)
                if result is not None:
                    print(result)
            elif command == "all":
                result = show_all(book)
                if result is not None:
                    print(result)
            elif command == "change":
                print(change_contact(args, book))
            elif command == "phone":
                print(show_phone(args, book))
            elif command == "add-birthday":
                print(add_birthday(args, book))
            elif command == "show-birthday":
                print(show_birthday(args, book))
            elif command == "birthdays":
                print(birthdays(book))
            else:
                print("Invalid command.")
        else:
            print("Please enter a command.")


if __name__ == "__main__":
    main()

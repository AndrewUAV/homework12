import re
import pickle as p
from datetime import datetime
from collections import UserDict


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Birthday(Field):
    def __init__(self, value):
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if is_valid_birthday(value):
            day, month, year = value.split(".")
            new_value = datetime(day=int(day), month=int(month), year=int(year))
            self.__value = new_value
        else:
            raise ValueError

    def __repr__(self):
        return f'{self.value.strftime("%d %B %Y")}'


class Name(Field):
    def __init__(self, value) -> None:
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value


class Phone(Field):
    def __init__(self, value):
        self.__value = None
        self.value = value

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        if is_valid_phone(value) and value.isdigit() and len(value) == 10:
            self.__value = value
        else:
            raise ValueError

    def __repr__(self):
        return f'{self.value}'


class Record:
    def __init__(self, name, phone=None, birthday=None):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(birthday) if birthday else None
        if phone is not None:
            self.phones.append(Phone(phone))

    def days_to_birthday(self, current_date=None):
        if not current_date:
            current_date = datetime.now().date()

        if self.birthday:
            next_birthday = datetime.strptime(str(self.birthday), '%d.%m.%Y').date().replace(year=current_date.year)

            if current_date > next_birthday:
                next_birthday = next_birthday.replace(year=current_date.year + 1)

            days_remaining = (next_birthday - current_date).days
            return f"Days till the next Birthday for {self.name}: {days_remaining} days"
        else:
            return "Birth date not added"

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                self.phones.remove(p)
                return
        raise ValueError

    def edit_phone(self, old_phone, new_phone):
        for i in self.phones:
            if i.value == old_phone:
                i.value = new_phone
                return f'Number {old_phone} from {self.name}`s list changed to {new_phone}'
            else:
                raise ValueError(f'phone {old_phone} is not find for name {self.name}')
        return f'Number {old_phone} is not exist in {self.name} list'

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def __str__(self):
        return f"Name: {self.name.value}, phones: {', '.join(str(p) for p in self.phones)}"


class AddressBook(UserDict):
    def __iter__(self, n):
        self.n = n
        self.count = 0
        return self

    def __next__(self):
        self.count += 1
        if self.count > self.n:
            raise StopIteration
        else:
            for i in self.data:
                yield self.data[i]

    def search_contact(self, query):
        matching_contacts = list()

        # Check if the query matches any phone numbers
        for record in self.data.values():
            for phone in record.phones:
                if query in phone.value:
                    matching_contacts.append(record)
                    break

        # Check if the query matches any names
        for record in self.data.values():
            if query.lower() in record.name.value.lower():
                matching_contacts.append(record)

        return matching_contacts

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]

    def save_data_to_disk(self, filename='address_book.pickle'):
        with open(filename, 'wb') as file:
            p.dump(self.data, file)

    def load_data_from_disk(self, filename='address_book.pickle'):
        try:
            with open(filename, 'rb') as file:
                self.data = p.load(file)
        except FileNotFoundError:
            return f'file {func_delete} not find.'

    def __str__(self) -> str:
        return "\n".join(str(r) for r in self.data.values())


def input_error(func):
    def inner(*args):
        try:
            return func(*args)
        except IndexError:
            return "Not enough params"
        except KeyError:
            return f"There is no contact such in phone book."
        except ValueError:
            return "Not enough params or wrong phone format"

    return inner


@input_error
def func_search_contacts(*args):
    query = args[0]
    matching_contacts = address_book.search_contact(query)

    if matching_contacts:
        result = '\n'.join(str(record) for record in matching_contacts)
        return f'Matching contacts: \n{result}'
    else:
        return  f'No contacts found for query: {query}'


@input_error
def is_valid_phone(phone):
    pattern = '\d{10}'
    searcher = re.findall(pattern, str(phone))
    phone = searcher[0]
    if phone == searcher[0]:
        return True
    else:
        return False


@input_error
def is_valid_birthday(value):
    pattern = '\d{2}\.\d{2}\.\d{4}'
    search = re.findall(pattern,value)
    if value == search[0]:
        day, month, year = value.split(".")
        try:
            new_value = datetime(day=int(day),month=int(month),year=int(year))
            return True
        except ValueError:
            return False
    else:
        return False


@input_error
def func_help():
    return ('Hi! If you want to start working, just enter "hello"\n' +
            'Number phone in 10 numbers, for example 0001230001\n' +
            'The representation of all commands looks as follows:\n' +
            '"hello" - start work with bot\n' +
            '"add" name phone\n' +
            '"change" name old_phone new_phone\n' +
            '"phone" name\n' +
            '"show all" - for show all information\n' +
            '"good bye", "close", "exit" - for end work\n' +
            '"delete" - delete info of name\n' +
            '"search" - command for search. Just enter "search" and something about contact like name or phone')


@input_error
def parser(user_input: str):
    COMMANDS = {
        "Hello": func_hello,
        "Add ": func_add,
        "Change ": func_change,
        "Phone ": func_search,
        "Show All": func_show_all,
        "Delete ": func_delete,
        "Search ": func_search_contacts
    }

    user_input = user_input.title()

    for kw, command in COMMANDS.items():
        if user_input.startswith(kw):
            return command, user_input[len(kw):].strip().split()
    return func_unknown_command, []


@input_error
def func_add(*args):
    name = args[0]
    record = Record(name)
    phone_numbers = args[1:]
    for phone_number in phone_numbers:
        record.add_phone(phone_number)
    address_book.add_record(record)
    return "Info saved successfully."


@input_error
def func_change(*args):
    for k, v in address_book.items():
        if k == args[0]:
            rec = address_book[args[0]]
            return rec.edit_phone(args[1], args[2])
    return f'{args[0]} isn`t exist in list of names'


@input_error
def func_delete(*args):
    name = args[0]

    if name in address_book:
        address_book.delete(name)
        return f"User {name} has been deleted from the phone book"
    else:
        return f'User {name} is not in the address book'


@input_error
def func_search(*args):
    name = args[0]
    record = address_book.find(name)
    if record:
        return str(record)
    else:
        raise KeyError


@input_error
def func_show_all(*args):
    return str(address_book)


@input_error
def func_unknown_command():
    return "Unknown command. Try again."


@input_error
def func_hello():
    return "How can I help you?"


@input_error
def func_quit():
    return "Good bye!"


address_book = AddressBook()


def main():
    print(func_help())

    # load data from disk if data is available
    address_book.load_data_from_disk()

    while True:
        user_input = input('Please, enter the valid command: ')

        if user_input.lower() in ["exit", "close", "good bye"]:
            address_book.save_data_to_disk()
            print(func_quit())
            break
        else:
            handler, arguments = parser(user_input)
            print(handler(*arguments))


if __name__ == '__main__':
    main()
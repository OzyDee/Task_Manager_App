import json
import hashlib
import datetime
import re
import sys
import getpass
from typing import List, Dict, Optional
import msvcrt


class SubTask:
    """
    Represents a sub-task within a main task.

    Attributes:
        details (str): The details of the sub-task.
        due_date (Optional[datetime.datetime]): The due date of the sub-task.
        priority (str): The priority of the sub-task.
        class_code (str): The class code associated with the sub-task.
        completed (bool): The completion status of the sub-task.
    """

    def __init__(self, details: str, due_date: Optional[str], priority: str, class_code: str, completed: bool = False):
        self.details = details
        self.due_date = datetime.datetime.strptime(due_date, '%d/%m/%Y') if due_date else None
        self.priority = priority
        self.class_code = class_code
        self.completed = completed

    def mark_as_completed(self):
        """Marks the sub-task as completed."""
        self.completed = True

    def to_dict(self) -> Dict[str, object]:
        """Converts the sub-task to a dictionary format."""
        return {
            "details": self.details,
            "due_date": self.due_date.strftime('%d/%m/%Y') if self.due_date else None,
            "priority": self.priority,
            "class_code": self.class_code,
            "completed": self.completed
        }

    @staticmethod
    def from_dict(data: Dict[str, object]) -> 'SubTask':
        """Creates a sub-task from a dictionary format."""
        return SubTask(
            details=str(data["details"]),
            due_date=str(data["due_date"]),
            priority=str(data["priority"]),
            class_code=str(data["class_code"]),
            completed=bool(data["completed"])
        )


class MainTask:

    def __init__(self, name: str, due_date: Optional[str], priority: str, status: str = "Not Started", class_code: Optional[str] = None):
        self.name = name
        self.due_date = datetime.datetime.strptime(due_date, '%d/%m/%Y') if due_date else None
        self.priority = priority
        self.status = status
        self.class_code = class_code
        self.sub_tasks: List[SubTask] = []

    def add_sub_task(self, sub_task: SubTask):
        """Adds a sub-task to the main task."""
        if self.due_date and sub_task.due_date and sub_task.due_date > self.due_date:
            raise ValueError("Sub-task due date cannot be after the main task due date.")
        self.sub_tasks.append(sub_task)

    def delete_sub_task(self, sub_task_index: int):
        """Deletes a sub-task from the main task."""
        if 1 <= sub_task_index <= len(self.sub_tasks):
            del self.sub_tasks[sub_task_index - 1]
        else:
            raise IndexError("Sub-task index out of range.")

    def mark_sub_task_as_completed(self, sub_task_index: int):
        """Marks a sub-task as completed."""
        if 1 <= sub_task_index <= len(self.sub_tasks):
            self.sub_tasks[sub_task_index - 1].mark_as_completed()
        else:
            raise IndexError("Sub-task index out of range.")

    def edit_sub_task(self, sub_task_index: int, details: Optional[str] = None, due_date: Optional[str] = None, priority: Optional[str] = None):
        """Edits a sub-task."""
        if 1 <= sub_task_index <= len(self.sub_tasks):
            sub_task = self.sub_tasks[sub_task_index - 1]
            if details:
                sub_task.details = details
            if due_date:
                new_due_date = datetime.datetime.strptime(due_date, '%d/%m/%Y')
                if self.due_date and new_due_date > self.due_date:
                    raise ValueError("Sub-task due date cannot be after the main task due date.")
                sub_task.due_date = new_due_date
            if priority:
                sub_task.priority = priority
        else:
            raise IndexError("Sub-task index out of range.")

    def mark_as_completed(self):
        """Marks the main task as completed."""
        self.status = "Completed"

    def view_sub_tasks(self) -> List[SubTask]:
        """Returns the list of sub-tasks."""
        return self.sub_tasks; List[SubTask] = []

    def search_sub_tasks(self, keyword: Optional[str] = None) -> List[SubTask]:
        """Searches for sub-tasks containing the specified keyword."""
        if keyword:
            keyword = keyword.lower()
            return [sub_task for sub_task in self.sub_tasks if keyword in sub_task.details.lower()]
        return self.sub_tasks  # Return all sub-tasks if no keyword is provided

    def to_dict(self) -> Dict[str, object]:
        """Converts the main task to a dictionary format."""
        return {
            "name": self.name,
            "due_date": self.due_date.strftime('%d/%m/%Y') if self.due_date else None,
            "priority": self.priority,
            "status": self.status,
            "class_code": self.class_code,
            "sub_tasks": [sub_task.to_dict() for sub_task in self.sub_tasks]
        }

    @staticmethod
    def from_dict(data: Dict[str, object]) -> 'MainTask':
        """Creates a main task from a dictionary format."""
        main_task = MainTask(
            name=str(data["name"]),
            due_date=str(data["due_date"]),
            priority=str(data["priority"]),
            status=str(data["status"]),
            class_code=str(data.get("class_code"))
        )
        main_task.sub_tasks = [SubTask.from_dict(sub_task_data) for sub_task_data in data["sub_tasks"]]
        return main_task


class Student:

    def __init__(self, student_id: str, password: str, task_lists: Optional[List[MainTask]] = None, is_hashed: bool = False):
        self.student_id = student_id
        self.password = self.hash_password(password) if not is_hashed else password
        self.task_lists: List[MainTask] = task_lists if task_lists else []

    @staticmethod
    def hash_password(password: str) -> str:
        """Hashes the password using SHA-256 with a salt."""
        salt = hashlib.sha256(password.encode()).hexdigest()[:16]
        return hashlib.sha256((salt + password).encode()).hexdigest() + ':' + salt

    def verify_password(self, password: str) -> bool:
        """Verifies the password against the stored hashed password."""
        stored_password, salt = self.password.split(':')
        return stored_password == hashlib.sha256((salt + password).encode()).hexdigest()

    def add_task_list(self, task_list: MainTask):
        """Adds a main task to the student's task list."""
        self.task_lists.append(task_list)

    def delete_task_list(self, list_index: int):
        """Deletes a main task from the student's task list."""
        if 1 <= list_index <= len(self.task_lists):
            del self.task_lists[list_index - 1]
        else:
            raise IndexError("Task list index out of range.")

    def edit_task_list(self, list_index: int, name: Optional[str] = None, due_date: Optional[str] = None, priority: Optional[str] = None, status: Optional[str] = None, class_code: Optional[str] = None):
        """Edits a main task in the student's task list."""
        if 1 <= list_index <= len(self.task_lists):
            task_list = self.task_lists[list_index - 1]
            if name:
                task_list.name = name
            if due_date:
                task_list.due_date = datetime.datetime.strptime(due_date, '%d/%m/%Y')
            if priority:
                task_list.priority = priority
            if status:
                task_list.status = status
            if class_code:
                task_list.class_code = class_code
        else:
            raise IndexError("Task list index out of range.")

    def view_task_lists(self) -> List[MainTask]:
        """Returns the list of main tasks."""
        return self.task_lists

    def view_all_sub_tasks(self) -> List[SubTask]:
        """Returns all sub-tasks from all main tasks."""
        all_sub_tasks: List[SubTask] = []
        for task_list in self.task_lists:
            all_sub_tasks.extend(task_list.view_sub_tasks())
        return all_sub_tasks

    def to_dict(self) -> Dict[str, object]:
        """Converts the student to a dictionary format."""
        return {
            "password": self.password,
            "task_lists": [task_list.to_dict() for task_list in self.task_lists]
        }

    @staticmethod
    def from_dict(student_id: str, data: Dict[str, object]) -> 'Student':
        """Creates a student from a dictionary format."""
        task_lists = [MainTask.from_dict(task_list_data) for task_list_data in data.get("task_lists", [])]
        return Student(student_id, str, data["password"], task_lists, is_hashed=True)


class StudentDatabase:

    def __init__(self, filename: str = "students.json"):
        self.filename = filename
        self.students: Dict[str, Student] = self.load_students()

    def load_students(self) -> Dict[str, Student]:
        """Loads students from the JSON file."""
        try:
            with open(self.filename, "r") as file:
                data = json.load(file)
                return {student_id: Student.from_dict(student_id, student_data) for student_id, student_data in data.items()}
        except FileNotFoundError:
            print(f"File '{self.filename}' not found. Creating a new student database.")
            return {}
        except json.JSONDecodeError:
            print("Error decoding JSON. The file might be corrupted.")
            return {}
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {}

    def save_students(self):
        """Saves students to the JSON file."""
        try:
            data = {student_id: student.to_dict() for student_id, student in self.students.items()}
            with open(self.filename, "w") as file:
                json.dump(data, file, indent=4)
        except Exception as e:
            print(f"An error occurred while saving: {e}")

    def get_student(self, student_id: str, password: str) -> Optional[Student]:
        """Retrieves a student by ID and verifies the password."""
        student = self.students.get(student_id)
        if student and student.verify_password(password):
            return student
        return None

    def add_student(self, student: Student):
        """Adds a new student to the database."""
        self.students[student.student_id] = student
        self.save_students()


def get_int_input(prompt: str) -> int:
    """Gets an integer input from the user."""
    while True:
        try:
            value = int(input(prompt))
            return value
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def get_priority_input(prompt: str) -> str:
    """Gets a priority input from the user."""
    priorities = {'H': 'High', 'M': 'Medium', 'L': 'Low'}
    while True:
        value = input(f"{prompt} (H: High, M: Medium, L: Low): ").strip().upper()
        if value in priorities:
            return priorities[value]
        print("Invalid input. Please enter a valid priority (H/M/L).")


def get_status_input(prompt: str) -> str:
    """Gets a status input from the user."""
    statuses = {'N': 'Not Started', 'P': 'In Progress', 'C': 'Completed'}
    while True:
        value = input(f"{prompt} (N: Not Started, P: In Progress, C: Completed): ").strip().upper()
        if value in statuses:
            return statuses[value]
        print("Invalid input. Please enter a valid status (N/P/C).")


def get_date_input(prompt: str, main_task_due_date: Optional[datetime.datetime] = None) -> Optional[str]:
    """Gets a date input from the user."""
    while True:
        value = input(f"{prompt} (leave empty to skip): ").strip()
        if value == "":
            return None
        try:
            due_date = datetime.datetime.strptime(value, '%d/%m/%Y')
            if main_task_due_date is None and due_date < datetime.datetime.now():
                print("Entered date is in the past. Please enter a future date.")
            elif main_task_due_date and due_date > main_task_due_date:
                print("Sub-task due date cannot be after the main task due date.")
            else:
                return value
        except ValueError:
            print("Invalid date format. Please enter the date in dd/mm/yyyy format.")


def get_class_code_input(prompt: str) -> Optional[str]:
    """Gets a class code input from the user."""
    while True:
        value = input(prompt).strip().upper()
        if value == '':
            return None
        if re.match(r'^[A-Z]{3}\d{3}$', value):
            return value
        print("Invalid input. Please enter a valid class code (e.g., ICT120) or leave it blank.")


def confirm_action(prompt: str) -> bool:
    """Confirms an action from the user."""
    while True:
        response = input(f"{prompt} (yes/no): ").strip().lower()
        if response in ['yes', 'no']:
            return response == 'yes'
        print("Invalid input. Please enter 'yes' or 'no'.")


def display_all_tasks(student: Student):
    """Displays all tasks and sub-tasks."""
    for i, task_list in enumerate(student.view_task_lists(), start=1):
        print(f"Task.{i}.")
        print("   |----------------------------------------------|------------|----------|------------|---------------|")
        print("   | #  |               Task Name                 | Due Date   | Priority | Class Code |    Status     |")
        print("   |----------------------------------------------|------------|----------|------------|---------------|")
        due_date_str = task_list.due_date.strftime('%d/%m/%Y') if task_list.due_date else 'N/A'
        print(f"   | {str(i).center(2)} | {task_list.name.center(39)} | {due_date_str.center(10)} | {task_list.priority.center(8)} | {(task_list.class_code if task_list.class_code else 'N/A').center(10)} | {task_list.status.center(13)} |")
        print("   |----------------------------------------------|------------|----------|------------|---------------|")

        if task_list.sub_tasks:
            print("   | #  |            Sub Task Details             | Due Date   | Priority | Class Code |    Status     |")
            print("   |----|-----------------------------------------|------------|----------|------------|---------------|")
            for j, sub_task in enumerate(task_list.view_sub_tasks(), start=1):
                status = 'Completed' if sub_task.completed else 'Not Completed'
                sub_due_date_str = sub_task.due_date.strftime('%d/%m/%Y') if sub_task.due_date else 'N/A'
                print(f"   | {str(j).center(2)} | {sub_task.details.center(39)} | {sub_due_date_str.center(10)} | {sub_task.priority.center(8)} | {(sub_task.class_code if sub_task.class_code else 'N/A').center(10)} | {status.center(13)} |")
            print("   |---------------------------------------------------------------------------------------------------|")
        print()


def display_task_lists(student: Student):
    """Displays all main tasks."""
    print("   |----------------------------------------------|------------|----------|------------|---------------|")
    print("   | #  |               Task Name                 | Due Date   | Priority | Class Code |   Status      |")
    print("   |----------------------------------------------|------------|----------|------------|---------------|")
    for i, task_list in enumerate(student.view_task_lists(), start=1):
        due_date_str = task_list.due_date.strftime('%d/%m/%Y') if task_list.due_date else 'N/A'
        print(f"   | {str(i).center(2)} | {task_list.name.center(39)} | {due_date_str.center(10)} | {task_list.priority.center(8)} | {(task_list.class_code if task_list.class_code else 'N/A').center(10)} |  {task_list.status.center(12)} |")
        print("   |----------------------------------------------|------------|----------|------------|---------------|")
    print()


def display_all_sub_tasks(student: Student):
    """Displays all sub-tasks from all main tasks."""
    all_sub_tasks = student.view_all_sub_tasks()
    if all_sub_tasks:
        print("   |---------------------------------------------------------------------------------------------------|")
        print("   | #  |            Sub Task Details             | Due Date   | Priority | Class Code |   Status      |")
        print("   |----|-----------------------------------------|------------|----------|------------|---------------|")
        for j, sub_task in enumerate(all_sub_tasks, start=1):
            status = 'Completed' if sub_task.completed else 'Not Completed'
            sub_due_date_str = sub_task.due_date.strftime('%d/%m/%Y') if sub_task.due_date else 'N/A'
            print(f"   | {str(j).center(2)} | {sub_task.details.center(39)} | {sub_due_date_str.center(10)} | {sub_task.priority.center(8)} | {(sub_task.class_code if sub_task.class_code else 'N/A').center(10)} | {status.center(13)} |")
        print("   |---------------------------------------------------------------------------------------------------|")
    else:
        print("   No sub-tasks found.")


def display_search_results(results: List[SubTask]):
    """Displays the results of a sub-task search."""
    if results:
        print("   |---------------------------------------------------------------------------------------------------|")
        print("   | #  |            Sub Task Details             | Due Date   | Priority | Class Code |   Status      |")
        print("   |----|-----------------------------------------|------------|----------|------------|---------------|")
        for j, sub_task in enumerate(results, start=1):
            status = 'Completed' if sub_task.completed else 'Not Completed'
            sub_due_date_str = sub_task.due_date.strftime('%d/%m/%Y') if sub_task.due_date else 'N/A'
            print(f"   | {str(j).center(2)} | {sub_task.details.center(39)} | {sub_due_date_str.center(10)} | {sub_task.priority.center(8)} | {(sub_task.class_code if sub_task.class_code else 'N/A').center(10)} | {status.center(13)} |")
        print("   |---------------------------------------------------------------------------------------------------|")
    else:
        print("   No sub-tasks found matching the criteria.")


def search_tasks(student: Student):
    """Allows the user to search for sub-tasks."""
    if not student.view_task_lists():
        print("No task lists available to search sub-tasks in.")
        return
    display_task_lists(student)
    search_all = input("Do you want to search across all lists? (yes/no): ").strip().lower()
    keyword = input("Enter keyword to search (leave empty to skip): ").strip()
    results = []
    if search_all == 'yes':
        for task_list in student.view_task_lists():
            results.extend(task_list.search_sub_tasks(keyword=keyword))
    else:
        list_index = get_int_input("Enter task list number to search in: ")
        if 1 <= list_index <= len(student.task_lists):
            results = student.task_lists[list_index - 1].search_sub_tasks(keyword=keyword)
        else:
            print("Invalid task list number.")
            return
    display_search_results(results)


def edit_sub_task(student: Student):
    """Allows the user to edit a sub-task."""
    if not student.view_task_lists():
        print("No task lists available to edit sub-tasks in.")
        return
    display_task_lists(student)
    list_index = get_int_input("Enter task list number to edit sub-task in: ")
    if 1 <= list_index <= len(student.task_lists):
        task_list = student.task_lists[list_index - 1]
        if task_list.view_sub_tasks():
            for i, sub_task in enumerate(task_list.view_sub_tasks(), start=1):
                print(f"{i}. {sub_task.details}")
            sub_task_index = get_int_input("Enter sub-task number to edit: ")
            if 1 <= sub_task_index <= len(task_list.sub_tasks):
                details = input("Enter new sub-task details (leave empty to skip): ")
                due_date = get_date_input("Enter new due date (dd/mm/yyyy, leave empty to skip): ", task_list.due_date) if input("Change due date? (yes/no): ").strip().lower() == 'yes' else None
                priority = get_priority_input("Enter new priority (H/M/L, leave empty to skip): ") if input("Change priority? (yes/no): ").strip().lower() == 'yes' else None
                task_list.edit_sub_task(sub_task_index, details=details or None, due_date=due_date, priority=priority)
            else:
                print("Invalid sub-task number.")
        else:
            print("No sub-tasks in this list.")
    else:
        print("Invalid task list number.")


def edit_task_list(student: Student):
    """Allows the user to edit a main task."""
    if not student.view_task_lists():
        print("No task lists available to edit.")
        return
    display_task_lists(student)
    list_index = get_int_input("Enter task list number to edit: ")
    if 1 <= list_index <= len(student.task_lists):
        new_name = input("Enter new task list name (leave empty to skip): ")
        new_due_date = get_date_input("Enter new due date (dd/mm/yyyy, leave empty to skip): ") if input("Change due date? (yes/no): ").strip().lower() == 'yes' else None
        new_priority = get_priority_input("Enter new priority (H/M/L, leave empty to skip): ") if input("Change priority? (yes/no): ").strip().lower() == 'yes' else None
        new_status = get_status_input("Enter new status (N/P/C, leave empty to skip): ") if input("Change status? (yes/no): ").strip().lower() == 'yes' else None
        new_class_code = get_class_code_input("Enter new class code (e.g., ICT120, leave empty to skip): ") if input("Change class code? (yes/no): ").strip().lower() == 'yes' else None
        student.edit_task_list(list_index, name=new_name or None, due_date=new_due_date, priority=new_priority, status=new_status, class_code=new_class_code)
    else:
        print("Invalid task list number.")


def create_main_task(student: Student):
    """Creates a new main task."""
    name = input("Enter main task name: ")
    due_date = get_date_input("Enter main task due date (dd/mm/yyyy)")
    priority = get_priority_input("Enter priority")
    status = get_status_input("Enter status")
    class_code = get_class_code_input("Enter Class Code (e.g., ICT120, leave empty to skip): ")
    task_list = MainTask(name, due_date, priority, status, class_code)
    student.add_task_list(task_list)


def delete_main_task(student: Student):
    """Deletes a main task."""
    if not student.view_task_lists():
        print("No main tasks available to delete.")
        return
    display_task_lists(student)
    list_index = get_int_input("Enter main task number to delete: ")
    if 1 <= list_index <= len(student.task_lists):
        if confirm_action("Are you sure you want to delete this task?"):
            student.delete_task_list(list_index)
    else:
        print("Invalid main task number.")


def mark_main_task_as_completed(student: Student):
    """Marks a main task as completed."""
    if not student.view_task_lists():
        print("No main tasks available to mark as completed.")
        return
    display_task_lists(student)
    list_index = get_int_input("Enter main task number to mark as completed: ")
    if 1 <= list_index <= len(student.task_lists):
        student.task_lists[list_index - 1].mark_as_completed()
        print("Main task marked as completed.")
    else:
        print("Invalid main task number.")


def add_sub_task(student: Student):
    """Adds a sub-task to a main task."""
    if not student.view_task_lists():
        print("No main tasks available to add sub-tasks to.")
        return
    display_task_lists(student)
    list_index = get_int_input("Enter main task number to add sub-task to: ")
    if 1 <= list_index <= len(student.task_lists):
        details = input("Enter sub-task details: ")
        main_task_due_date = None
        if student.task_lists[list_index - 1].due_date:
            main_task_due_date = student.task_lists[list_index - 1].due_date
        due_date = get_date_input("Enter sub-task due date (dd/mm/yyyy): ", main_task_due_date)
        priority = get_priority_input("Enter priority")
        status = get_status_input("Enter status")
        class_code = student.task_lists[list_index - 1].class_code or "N/A"
        sub_task = SubTask(details, due_date, priority, class_code, completed=(status == 'C'))
        student.task_lists[list_index - 1].add_sub_task(sub_task)
    else:
        print("Invalid main task number.")


def delete_sub_task(student: Student):
    """Deletes a sub-task from a main task."""
    if not student.view_task_lists():
        print("No main tasks available to delete sub-tasks from.")
        return
    display_all_tasks(student)
    list_index = get_int_input("Enter main task number to delete sub-task from: ")
    if 1 <= list_index <= len(student.task_lists):
        task_list = student.task_lists[list_index - 1]
        if task_list.view_sub_tasks():
            for i, sub_task in enumerate(task_list.view_sub_tasks(), start=1):
                print(f"{i}. {sub_task.details}")
            sub_task_index = get_int_input("Enter sub-task number to delete: ")
            if 1 <= sub_task_index <= len(task_list.sub_tasks):
                if confirm_action("Are you sure you want to delete this sub-task?"):
                    task_list.delete_sub_task(sub_task_index)
            else:
                print("Invalid sub-task number.")
        else:
            print("No sub-tasks in this list.")
    else:
        print("Invalid main task number.")


def mark_sub_task_as_completed(student: Student):
    """Marks a sub-task as completed."""
    if not student.view_task_lists():
        print("No main tasks available to mark sub-tasks as completed.")
        return
    display_all_tasks(student)
    list_index = get_int_input("Enter main task number to mark sub-task as completed: ")
    if 1 <= list_index <= len(student.task_lists):
        task_list = student.task_lists[list_index - 1]
        if task_list.view_sub_tasks():
            for i, sub_task in enumerate(task_list.view_sub_tasks(), start=1):
                print(f"{i}. {sub_task.details}")
            sub_task_index = get_int_input("Enter sub-task number to mark as completed: ")
            if 1 <= sub_task_index <= len(task_list.sub_tasks):
                task_list.mark_sub_task_as_completed(sub_task_index)
            else:
                print("Invalid sub-task number.")
        else:
            print("No sub-tasks in this list.")
    else:
        print("Invalid main task number.")


def custom_password_input(prompt: str) -> str:
    """Prompts the user to enter a password with masked input."""
    if 'msvcrt' in sys.modules:
        print(prompt, end="", flush=True)
        password = ""
        while True:
            ch = msvcrt.getch()
            if ch in (b'\r', b'\n'):
                break
            if ch == b'\x08':  # backspace
                password = password[:-1]
                sys.stdout.write('\b \b')
                sys.stdout.flush()
            else:
                password += ch.decode('utf-8')
                sys.stdout.write('*')
                sys.stdout.flush()
        print()  # move to next line
        return password
    else:
        return getpass.getpass(prompt)


def main():
    """Main function to run the task management system."""
    database = StudentDatabase()

    student_id = input("Enter your student ID: ")

    student = database.students.get(student_id)

    if student:
        for attempt in range(3):
            password = custom_password_input("Enter your password: ")
            if student.verify_password(password):
                break
            else:
                print("Incorrect password.")
                if attempt < 2:
                    print(f"You have {2 - attempt} attempt(s) left.")
        else:
            print("It seems you have entered the wrong password multiple times. Please try again later or contact support.")
            exit()
    else:
        create_new = input("No account found with the provided student ID. Would you like to create a new student? (yes/no): ").strip().lower()
        if create_new == 'yes':
            password = custom_password_input("Enter a password: ")
            student = Student(student_id, password)
            database.add_student(student)
            print("New student created successfully.")
        else:
            exit()

    while True:
        print("\nMain Menu:")
        print("1. Task Management")
        print("2. Save and Exit")
        print("3. Exit without Saving")
        print("4. Help")
        choice = input("Choose an option: ").strip().lower()

        if choice == "1":
            task_management_menu(student)
        elif choice == "2":
            database.save_students()
            print("Changes saved successfully.")
            print("Goodbye! Keep up the good work and stay organised!")
            break
        elif choice == "3":
            print("Exiting without saving.")
            print("Goodbye! Remember, each day is a new opportunity to do your best!")
            break
        elif choice == "4":
            display_help("main")
        else:
            print("Invalid choice. Please try again.")


def task_management_menu(student: Student):
    """Displays the task management menu."""
    while True:
        print("\nTask Management:")
        print("1. Create Main Task")
        print("2. Add Sub-Task to Main Task")
        print("3. Mark Tasks as Completed")
        print("4. View and Search")
        print("5. Edit Tasks")
        print("6. Delete Tasks")
        print("7. Back to Main Menu")
        print("8. Help")
        task_choice = input("Choose an option: ").strip().lower()

        if task_choice == "1":
            create_main_task(student)
        elif task_choice == "2":
            add_sub_task(student)
        elif task_choice == "3":
            mark_tasks_menu(student)
        elif task_choice == "4":
            view_and_search_menu(student)
        elif task_choice == "5":
            edit_menu(student)
        elif task_choice == "6":
            delete_menu(student)
        elif task_choice == "7":
            break
        elif task_choice == "8":
            display_help("task_management")
        else:
            print("Invalid choice. Please try again.")


def mark_tasks_menu(student: Student):
    """Displays the menu for marking tasks as completed."""
    while True:
        print("\nMark as Completed:")
        print("1. Mark Main Task as Completed")
        print("2. Mark Sub-Task as Completed")
        print("3. Back to Task Management Menu")
        mark_choice = input("Choose an option: ").strip().lower()

        if mark_choice == "1":
            mark_main_task_as_completed(student)
        elif mark_choice == "2":
            mark_sub_task_as_completed(student)
        elif mark_choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")


def view_and_search_menu(student: Student):
    """Displays the menu for viewing and searching tasks."""
    while True:
        print("\nView and Search:")
        print("1. View All Tasks and Sub-Tasks")
        print("2. View Main Tasks")
        print("3. View Sub-Tasks")
        print("4. Search Sub-Tasks")
        print("5. Back to Task Management Menu")
        view_choice = input("Choose an option: ").strip().lower()

        if view_choice == "1":
            display_all_tasks(student)
        elif view_choice == "2":
            display_task_lists(student)
        elif view_choice == "3":
            display_all_sub_tasks(student)
        elif view_choice == "4":
            search_tasks(student)
        elif view_choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")


def edit_menu(student: Student):
    """Displays the menu for editing tasks."""
    while True:
        print("\nEdit:")
        print("1. Edit Main Task")
        print("2. Edit Sub-Task")
        print("3. Back to Task Management Menu")
        edit_choice = input("Choose an option: ").strip().lower()

        if edit_choice == "1":
            edit_task_list(student)
        elif edit_choice == "2":
            edit_sub_task(student)
        elif edit_choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")


def delete_menu(student: Student):
    """Displays the menu for deleting tasks."""
    while True:
        print("\nDelete:")
        print("1. Delete Main Task")
        print("2. Delete Sub-Task")
        print("3. Back to Task Management Menu")
        delete_choice = input("Choose an option: ").strip().lower()

        if delete_choice == "1":
            delete_main_task(student)
        elif delete_choice == "2":
            delete_sub_task(student)
        elif delete_choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")


def display_help(menu: str):
    """Displays the help menu for the specified section."""
    help_texts = {
        "main": """
Main Menu Help:
1. Task Management: Manage your tasks and sub-tasks.
2. Save and Exit: Save all changes and exit the application.
3. Exit without Saving: Exit the application without saving changes.
4. Help: Display this help message.
        """,
        "task_management": """
Task Management Menu Help:
1. Create Main Task: Create a new main task.
2. Add Sub-Task to Main Task: Add a sub-task to an existing main task.
3. Mark Tasks as Completed: Mark main tasks or sub-tasks as completed.
4. View and Search: View all tasks and sub-tasks or search for specific sub-tasks.
5. Edit Tasks: Edit an existing main task or sub-task.
6. Delete Tasks: Delete an existing main task or sub-task.
7. Back to Main Menu: Go back to the main menu.
8. Help: Display this help message.
        """
    }
    print(help_texts.get(menu, "No help available for this menu."))


if __name__ == "__main__":
    main()

import unittest
from task_manager import SubTask, MainTask, Student, StudentDatabase
import datetime

class TestSubTask(unittest.TestCase):

    def setUp(self):
        self.sub_task = SubTask("SubTask1", "01/01/2025", "High", "ICT123")

    def test_sub_task_creation(self):
        self.assertEqual(self.sub_task.details, "SubTask1")
        self.assertEqual(self.sub_task.due_date, datetime.datetime.strptime("01/01/2025", '%d/%m/%Y'))
        self.assertEqual(self.sub_task.priority, "High")
        self.assertEqual(self.sub_task.class_code, "ICT123")
        self.assertFalse(self.sub_task.completed)

    def test_mark_as_completed(self):
        self.sub_task.mark_as_completed()
        self.assertTrue(self.sub_task.completed)

    def test_to_dict(self):
        expected_dict = {
            "details": "SubTask1",
            "due_date": "01/01/2025",
            "priority": "High",
            "class_code": "ICT123",
            "completed": False
        }
        self.assertEqual(self.sub_task.to_dict(), expected_dict)

    def test_from_dict(self):
        data = {
            "details": "SubTask1",
            "due_date": "01/01/2025",
            "priority": "High",
            "class_code": "ICT123",
            "completed": False
        }
        sub_task = SubTask.from_dict(data)
        self.assertEqual(sub_task.details, "SubTask1")
        self.assertEqual(sub_task.due_date, datetime.datetime.strptime("01/01/2025", '%d/%m/%Y'))
        self.assertEqual(sub_task.priority, "High")
        self.assertEqual(sub_task.class_code, "ICT123")
        self.assertFalse(sub_task.completed)

class TestMainTask(unittest.TestCase):

    def setUp(self):
        self.main_task = MainTask("MainTask1", "01/01/2025", "High", "Not Started", "ICT123")
        self.sub_task = SubTask("SubTask1", "01/01/2025", "High", "ICT123")

    def test_main_task_creation(self):
        self.assertEqual(self.main_task.name, "MainTask1")
        self.assertEqual(self.main_task.due_date, datetime.datetime.strptime("01/01/2025", '%d/%m/%Y'))
        self.assertEqual(self.main_task.priority, "High")
        self.assertEqual(self.main_task.status, "Not Started")
        self.assertEqual(self.main_task.class_code, "ICT123")
        self.assertEqual(self.main_task.sub_tasks, [])

    def test_add_sub_task(self):
        self.main_task.add_sub_task(self.sub_task)
        self.assertIn(self.sub_task, self.main_task.sub_tasks)

    def test_delete_sub_task(self):
        self.main_task.add_sub_task(self.sub_task)
        self.main_task.delete_sub_task(1)
        self.assertNotIn(self.sub_task, self.main_task.sub_tasks)

    def test_mark_sub_task_as_completed(self):
        self.main_task.add_sub_task(self.sub_task)
        self.main_task.mark_sub_task_as_completed(1)
        self.assertTrue(self.main_task.sub_tasks[0].completed)

    def test_to_dict(self):
        self.main_task.add_sub_task(self.sub_task)
        expected_dict = {
            "name": "MainTask1",
            "due_date": "01/01/2025",
            "priority": "High",
            "status": "Not Started",
            "class_code": "ICT123",
            "sub_tasks": [self.sub_task.to_dict()]
        }
        self.assertEqual(self.main_task.to_dict(), expected_dict)

    def test_from_dict(self):
        data = {
            "name": "MainTask1",
            "due_date": "01/01/2025",
            "priority": "High",
            "status": "Not Started",
            "class_code": "ICT123",
            "sub_tasks": [self.sub_task.to_dict()]
        }
        main_task = MainTask.from_dict(data)
        self.assertEqual(main_task.name, "MainTask1")
        self.assertEqual(main_task.due_date, datetime.datetime.strptime("01/01/2025", '%d/%m/%Y'))
        self.assertEqual(main_task.priority, "High")
        self.assertEqual(main_task.status, "Not Started")
        self.assertEqual(main_task.class_code, "ICT123")
        self.assertEqual(main_task.sub_tasks[0].to_dict(), self.sub_task.to_dict())

class TestStudent(unittest.TestCase):

    def setUp(self):
        self.student = Student("student1", "password123")
        self.main_task = MainTask("MainTask1", "01/01/2025", "High", "Not Started", "ICT123")

    def test_student_creation(self):
        self.assertEqual(self.student.student_id, "student1")
        self.assertTrue(self.student.verify_password("password123"))
        self.assertEqual(self.student.task_lists, [])

    def test_add_task_list(self):
        self.student.add_task_list(self.main_task)
        self.assertIn(self.main_task, self.student.task_lists)

    def test_delete_task_list(self):
        self.student.add_task_list(self.main_task)
        self.student.delete_task_list(1)
        self.assertNotIn(self.main_task, self.student.task_lists)

    def test_to_dict(self):
        self.student.add_task_list(self.main_task)
        expected_dict = {
            "password": self.student.password,
            "task_lists": [self.main_task.to_dict()]
        }
        self.assertEqual(self.student.to_dict(), expected_dict)

    def test_from_dict(self):
        data = {
            "password": self.student.password,
            "task_lists": [self.main_task.to_dict()]
        }
        student = Student.from_dict("student1", data)
        self.assertEqual(student.student_id, "student1")
        self.assertEqual(student.password, self.student.password)
        self.assertEqual(student.task_lists[0].to_dict(), self.main_task.to_dict())

class TestStudentDatabase(unittest.TestCase):

    def setUp(self):
        self.database = StudentDatabase(filename="test_students.json")
        self.student = Student("student1", "password123")
        self.database.add_student(self.student)

    def tearDown(self):
        import os
        if os.path.exists("test_students.json"):
            os.remove("test_students.json")

    def test_add_student(self):
        student = self.database.get_student("student1", "password123")
        self.assertIsNotNone(student)
        self.assertEqual(student.student_id, "student1")

    def test_save_and_load_students(self):
        self.database.save_students()
        loaded_database = StudentDatabase(filename="test_students.json")
        student = loaded_database.get_student("student1", "password123")
        self.assertIsNotNone(student)
        self.assertEqual(student.student_id, "student1")

if __name__ == '__main__':
    unittest.main()

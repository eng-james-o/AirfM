import sqlite3

class ProjectDatabase:
    def __init__(self, db_path="projects.db"):
        self.connection = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    location TEXT NOT NULL,
                    date TEXT NOT NULL
                )
                """
            )

    def add_project(self, name, location, date):
        with self.connection:
            self.connection.execute(
                "INSERT INTO projects (name, location, date) VALUES (?, ?, ?)",
                (name, location, date)
            )

    def get_projects(self):
        with self.connection:
            return self.connection.execute("SELECT name, location, date FROM projects").fetchall()

    def close(self):
        self.connection.close()

# Example usage
if __name__ == "__main__":
    db = ProjectDatabase()
    db.add_project("Project 1", "C:/Users", "12-16-25")
    db.add_project("Project 2", "C:/Users", "12-16-25")
    db.add_project("Project 3", "C:/Users", "12-16-25")
    print(db.get_projects())
    db.close()

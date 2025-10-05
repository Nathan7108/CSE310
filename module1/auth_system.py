import getpass
from database import Database

class AuthSystem:
    def __init__(self): 
        self.db = Database()
    
    def register(self):
        print("\n=== User Registration ===")
        username = input("Enter username: ").strip()
        
        if not username:
            print("Username cannot be empty!")
            return False
        
        password = getpass.getpass("Enter password: ")
        if len(password) < 6:
            print("Password must be at least 6 characters long!")
            return False
        
        email = input("Enter email (optional): ").strip()
        if not email:
            email = None
        
        success, message = self.db.register_user(username, password, email)
        print(message)
        return success
    
    def login(self):
        print("\n=== User Login ===")
        username = input("Enter username: ").strip()
        password = getpass.getpass("Enter password: ")
        
        success, message = self.db.login_user(username, password)
        print(message)
        
        if success:
            user_info = self.db.get_user_info(username)
            if user_info:
                print(f"\nUser Info:")
                print(f"ID: {user_info['id']}")
                print(f"Username: {user_info['username']}")
                print(f"Email: {user_info['email'] or 'Not provided'}")
                print(f"Created: {user_info['created_at']}")
        
        return success
    
    def show_all_users(self):
        print("\n=== All Users ===")
        users = self.db.get_all_users()
        
        if users:
            print(f"Total users: {len(users)}")
            print("-" * 60)
            print(f"{'ID':<3} | {'Username':<15} | {'Email':<25} | {'Created'}")
            print("-" * 60)
            for user in users:
                email = user[2] if user[2] else "None"
                print(f"{user[0]:<3} | {user[1]:<15} | {email:<25} | {user[3]}")
        else:
            print("No users found")
    
    def delete_user(self):
        print("\n=== Delete User ===")
        username = input("Enter username to delete: ").strip()
        
        if not username:
            print("Username cannot be empty!")
            return
        
        confirm = input(f"Are you sure you want to delete user '{username}'? (y/n): ").strip().lower()
        if confirm == 'y':
            success, message = self.db.delete_user(username)
            print(message)
        else:
            print("Deletion cancelled")
    
    def update_email(self):
        print("\n=== Update Email ===")
        username = input("Enter username: ").strip()
        new_email = input("Enter new email: ").strip()
        
        if not username or not new_email:
            print("Username and email cannot be empty!")
            return
        
        success, message = self.db.update_user_email(username, new_email)
        print(message)
    
    def show_menu(self):
        while True:
            print("\n=== Auth System ===")
            print("1. Register")
            print("2. Login")
            print("3. View All Users")
            print("4. Delete User")
            print("5. Update Email")
            print("6. Database Stats")
            print("7. Exit")
            
            choice = input("\nSelect an option (1-7): ").strip()
            
            if choice == "1":
                self.register()
            elif choice == "2":
                self.login()
            elif choice == "3":
                self.show_all_users()
            elif choice == "4":
                self.delete_user()
            elif choice == "5":
                self.update_email()
            elif choice == "6":
                count = self.db.get_user_count()
                print(f"\nDatabase Statistics:")
                print(f"Total users: {count}")
            elif choice == "7":
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please select 1-7.")

if __name__ == "__main__":
    auth = AuthSystem()
    auth.show_menu()

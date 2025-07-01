class UIHandler:
    def display_role_selection(self):
        print("=" * 60)
        print("🏥 HIPAA COMPLIANT MEDICAL SMART AGENT")
        print("=" * 60)
        print("Please select your role:")
        print("1. Doctor")
        print("2. Administrator")
        print("-" * 60)
        
        while True:
            choice = input("Select role (1/2): ").strip()
            if choice == "1":
                user_role = "doctor"
                print(f"Logged in as: Doctor")
                return user_role
            elif choice == "2":
                user_role = "administrator"
                print(f"Logged in as: Administrator")
                return user_role
            else:
                print("Invalid choice. Please select 1 or 2.")
    
    def get_greeting(self, user_role):
        if user_role == "doctor":return "Hi Doctor, let's get to know about your patients"
        else:return "Hi Admin, let's get to know about your patients"
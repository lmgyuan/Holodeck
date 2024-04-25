from openai import OpenAI
import os
from getpass import getpass

class InteractiveEdit:

    def __init__(self):
        self.num = []

    def addition(self):
        pass

    def deletion(self):
        pass

    def ask_input(self):

        if 'OPENAI_API_KEY' not in os.environ:
            print("You didn't set your OPENAI_API_KEY on the command line.")
            os.environ['OPENAI_API_KEY'] = getpass("Please enter your OpenAI API Key: ")

        client = OpenAI()

        while True:
            usr_input = input("Would you like to delete or add any object? Choose add, delete, or quit editing.")
            
            response = client.chat.completions.create(
            model="gpt-3.5",
            messages=[
                {
                "role": "system",
                "content": """
                You are helping a system to identify which mode the user chose.
                The mode could be delete, add, or quit.
                Output only one string, it could be delete, add, or quit.
                Make sure the output is only one word in lowercase that can be identified by a Python program.
                If the user inputs No Edit, it is likely to be quit.
                """
                },
                {
                "role": "user",
                "content": usr_input
                }
            ],
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )

            mode = response.choices[0].message.content.lowercase().strip()

            if mode == "add":
                self.additon()
            elif mode == "delete":
                self.deletion()
            else:
                print("Quit Editing.")
                break

import tkinter as tk
import subprocess
from threading import Thread
from tkinter import scrolledtext
from PIL import Image, ImageTk

key = "enter your own key"
process = None

class MultiPageApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        
        for F in (StartPage, ChatPage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame(StartPage)
    
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()


def display_text_and_image():
    # Display text
    output_label.config(text="Displaying Image and Text")

    # Open the image file
    image = Image.open("data/scenes/a_living_room-2024-04-30-12-03-02-071006/a_living_room.png")

    # Convert the image to a format compatible with Tkinter
    tk_image = ImageTk.PhotoImage(image)

    # Create a label to display the image
    image_label = tk.Label(root, image=tk_image)
    image_label.pack()

    # Keep a reference to the image to prevent it from being garbage collected
    image_label.image = tk_image

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        # Load an image
        image = tk.PhotoImage(file="logo.png")

        # Create and position an image widget
        resized_image = image.subsample(2)
        image_label = tk.Label(self, image=resized_image)
        image_label.image = resized_image
        image_label.pack(pady=15)

        label = tk.Label(self, text="Welcome!")
        label.pack(pady=15, padx=10)

        button1 = tk.Button(self, text="Let's make 3D environment",
                            command=lambda: controller.show_frame(ChatPage))
        button1.pack()


class ChatPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        # Load an image
        image = tk.PhotoImage(file="logo.png")

        # Create and position an image widget
        resized_image = image.subsample(2)
        image_label = tk.Label(self, image=resized_image)
        image_label.image = resized_image
        image_label.pack()

        border_frame = tk.Frame(self, bg="white",relief="solid")
        border_frame.pack(padx=10, pady=10)

        text_label = tk.Label(border_frame, text="Please write the description of the 3D environment you want below.", bg="#d65b00", fg="white", width=30, padx=10, pady=10, wraplength=300)
        text_label.pack(padx=5, pady=5)

        # Create and position the entry widget
        self.entry = tk.Entry(self, width=50)
        self.entry.pack(pady=10)

        # Create and position the submit button
        #submit_button = tk.Button(root, text="Display Text and Image", command=display_text_and_image)
        submit_button = tk.Button(self, text="Submit", command=self.submit_query)
        submit_button.pack()

        # Create and position the label to display output
        self.output_text = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=10, width=40)
        self.output_text.pack(pady=10)

    def submit_query(self):
        global process

        query = self.entry.get()
        self.entry.delete(0, tk.END)
        if query.lower() == 'quit' and process:
            process.terminate()  # Terminate the subprocess
            process = None  # Reset process to None for the next query
            self.output_text.delete('1.0', tk.END)
            #output_label.config(text="")
            print("done")
            return
        
        run_query=f"""main.py --query "{query}" --openai_api_key {key}"""

        print(run_query)
        # Use subprocess to open a zsh terminal and execute the query
        if not process:
            #process = subprocess.Popen(['python', query], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            process = subprocess.Popen(['python', "main.py", "--query", f"{query}", "--openai_api_key", key], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            Thread(target=self.read_stdout).start()
        else: 
            print("here")
        #process = subprocess.Popen(['zsh', '-c', query], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        process.stdin.write(query + '\n')
        process.stdin.flush()

    def read_stdout(self):
        global process

        # Read stdout line by line in real-time
        for line in process.stdout:
            line = line.strip()
            self.output_text.config(state=tk.NORMAL)  # Enable editing of text widget
            self.output_text.insert(tk.END, line + "\n")  # Append new line of output
            self.output_text.config(state=tk.DISABLED)  # Disable editing of text widget
            self.output_text.see(tk.END)  # Scroll to the end of text widget

# Start the main event loop
root = MultiPageApp()
root.mainloop()


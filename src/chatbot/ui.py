import tkinter as tk
from tkinter import PhotoImage
from PIL import Image, ImageTk
import os, sys
import customtkinter as ctk
import pystray
import mss
import mss.tools
import requests
import json
from capture_ui import capture
import executor as ex
from service import instruct

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("custom_theme.json")    
#ctk.set_default_color_theme("green")  
#icon_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "icons") #TODO auslagern zu settings
screen_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "screens") #TODO auslagern zu settings


class ChatbotApp(ctk.CTk):
    """
    Class for the Chatbot Application
    
    Attributes:
        title (str): The title of the application
        iconpath (str): The path to the icon of the application
        iconphoto (str): The photo of the icon of the application
        label_icon_path (str): The path to the icon of the label
        label_icon_image (str): The image of the icon of the label
        icon_label (str): The label with the icon
        label_user_path (str): The path to the user icon
        user_label (str): The user icon
        chat_history (str): The chat history
        input_field (str): The input field
        send_icon_image (str): The image of the send icon
        send_button (str): The send button
        verification (str): The verification
    
    """
    def __init__(self):
        super().__init__()
        self.title("A2C2")
        self.iconpath = ImageTk.PhotoImage(file=os.path.join(resource(os.path.join("icons","logo.png"))))
        self.wm_iconbitmap()
        self.iconphoto(False, self.iconpath)

        #self.protocol('WM_DELETE_WINDOW', self.minimize_to_tray)
        self.resizable(False, False)
        self.geometry("320x570-10-10")
        self.send_icon_image = ctk.CTkImage(Image.open(os.path.join(resource(os.path.join("icons","send.png")))), size=(25, 25))

        # Icon für das Label vorbereiten (Größe angepasst)
        self.label_icon_path = os.path.join("icons", "logo.png")
        self.label_icon_image = ctk.CTkImage(Image.open(self.label_icon_path), size=(50, 50))  # Größe hier angepasst

        # Label mit Icon hinzufügen, ohne Text
        self.icon_label = ctk.CTkLabel(self, image=self.label_icon_image, text="")
        self.icon_label.pack(pady=(10, 5))

        # agent label
        self.agent_label = ctk.CTkImage(Image.open(self.label_icon_path), size=(30, 30))  # Größe hier angepasst

        # Icon für das Label vorbereiten (Größe angepasst)
        self.label_user_path = os.path.join("icons", "user.png")
        self.user_label = ctk.CTkImage(Image.open(self.label_user_path), size=(30, 30))  # Größe hier angepasst


        self.chat_history = ctk.CTkScrollableFrame(self, width=290, height=430)
        self.chat_history.pack(padx=5, pady=5)

        self.input_field = ctk.CTkTextbox(self, width=250)
        self.input_field.pack(side=ctk.LEFT, padx=5, pady=(0,5))

        self.input_field.bind("<Shift-Return>", self.insert_newline)
        self.input_field.bind("<Return>", self.process_input)

        self.send_button = ctk.CTkButton(self, text="", image=self.send_icon_image, command=self.process_input, height=40, width=45)
        self.send_button.pack(side=ctk.LEFT, padx=5, pady=(0,5))
        self.verification = None
        self.create_chat_field("Hi, I am your agent A2C2 and I would like to do some work for you.\n"+
                                "\nPlease enter your instruction in the text box below.\n", is_user=False)

    # Function to insert a newline when Shift+Return isß pressed
    def insert_newline(self, event):
        """
        Inserts a newline when Shift+Return is pressed.
        Args:
            event (str): The event.
        """
        event.widget.insert("insert", "\n")
        return "break"
    
    def minimize_to_tray(self):
        """
        Minimizes the window to the system tray.
        """
        self.withdraw()
        image = Image.open(os.path.join(resource(os.path.join("icons","logo.png"))))
        menu = (pystray.MenuItem('Quit',  self.quit_window), 
                pystray.MenuItem('Show',self.show_window))
        icon = pystray.Icon("name", image, "A2C2", menu)
        icon.run()

    def quit_window(self, icon):
        """ 
        Quits the window.
        Args:
            icon (str): The icon.
        """
        icon.stop()
        self.destroy()

    def show_window(self, icon):
        """
        Shows the window.
        Args:
            icon (str): The icon.
        """
        icon.stop()
        self.after(0,self.deiconify)

    def process_input(self, event=None):
        """
        Processes the user input and sends it to the server for processing.
        Args:
            event (str): The event.
            
        Returns:
                str: The user input.    
        """
        user_input = self.input_field.get("1.0","end-1c")
        self.input_field.delete("1.0", "end")
        self.create_chat_field(text=user_input)
        instruction = {"instruction_text": user_input}
        for i in range(1):
            print("Instruction", instruction)
            instruction, status_code = instruct({'instruction': json.dumps(instruction)}, capture())
            if instruction is None or not status_code == 200:
                self.create_chat_field("No more subinstructions to execute. Please enter next instruction.", is_user=False)
                return
            if not status_code == 200:
                self.create_chat_field("An error has occured please retry", is_user=False)
                return
            
            print(instruction)
            #print(instruction['id'])
            # print(instruction['subtasks'])
            
            # url = 'http://127.0.0.1:8000/instruct'
            # instruction = {'instruction': json.dumps({"instruction_text": user_input})}
            # files = capture()
            # print("finished capturing")
            # resp = requests.post(url=url, data=instruction, files=files) 
            # print("before json", resp.json())
            # call executor with the json response
            for subtask in instruction['subtasks'][instruction['subtask_pointer']:]:
                print("subtask is executed:", subtask)
                action_type, component, additional_info = ex.from_json(subtask)
                print("after json", action_type, component, additional_info, len(component))
                ex.execute_action(action_type, component, additional_info)
                instruction["subtask_pointer"] += 1
                self.create_chat_field(str(action_type) + str(subtask) + additional_info, is_user=False)
            instruction["subinstructions_pointer"] += 1

        # self.capture_screen()
        #self.create_chat_field(text=user_input, image=Image.open("protimemobile.png"), is_user=False)
        #self.create_verification_field()
        return "break"
    
    def create_chat_field(self, text, image=None, is_user=True):
        """
        Creates a chat field with text and image.
        Args:
            text (str): The text.
            image (str): The image.
            is_user (bool): True if the user is the sender, False if the agent is the sender.
        """
        side = ctk.RIGHT if is_user else ctk.LEFT
        user_color = "#E175B4"  # Color for user messages
        agent_color = "#B2FCB2"  # Color for agent messages
        bg_color = user_color if is_user else agent_color

        wrapper = ctk.CTkFrame(self.chat_history)
        wrapper.pack(side=ctk.TOP, fill="x")

        frame = ctk.CTkFrame(wrapper, fg_color=bg_color)
        frame.pack(side=side, padx=5, pady=5)

        # Imageprocessing
        if image:
            calc_aspect_ratio = image.size[0] / 140
            image_resized = Image.open(image).resize((140, int(image.size[1] / calc_aspect_ratio)))
            photo_image = ImageTk.PhotoImage(image_resized)
            image = ctk.CTkImage(master=frame, image=photo_image)
        
        # label with user icon and text or agent icon and text
        if is_user:
            label = ctk.CTkLabel(frame, image=self.user_label, text=text, wraplength=140, justify="left", compound=ctk.TOP)
        else:
            label = ctk.CTkLabel(frame, image=self.agent_label, text=text, wraplength=140, justify="left", compound=ctk.TOP)

        label.pack(padx=5, pady=1)

    def create_verification_field(self, text, ):
        """
        Creates a verification field.
        Args:
            text (str): The text. 
        """
        wrapper = ctk.CTkFrame(self.chat_history)
        wrapper.pack(side=ctk.TOP, fill="x")
        label = ctk.CTkLabel(wrapper, text=text, wraplength=140, compound=ctk.TOP)
        label.pack(padx=5, pady=4)
        confirm_button = ctk.CTkButton(wrapper, text="Yes", fg_color="green", command=lambda: self.verify(confirm_button, refuse_button, True))
        confirm_button.pack(side=ctk.LEFT, padx=5, pady=(0,5))
        refuse_button = ctk.CTkButton(wrapper, text="No", fg_color="red", command=lambda: self.verify(confirm_button, refuse_button, False))
        refuse_button.pack(side=ctk.LEFT, padx=5, pady=(0,5))

    def verify(self, confirm_button, refuse_button, is_verified):
        """
        Verifies the action.
        Args:
            confirm_button (str): The confirm button.
            refuse_button (str): The refuse button.
            is_verified (bool): True if the action is verified, False if the action is refused.
        """
        if is_verified:
            confirm_button.configure(state="disabled")
            refuse_button.pack_forget()
        else:
            refuse_button.configure(state="disabled")
            confirm_button.pack_forget()


def resource(relative_path):
    """
    Get the absolute path to a resource by specifying the relative path.
    Args:
        relative_path (str): The relative path to the resource.
    Returns:
        str: The absolute path to the resource.
    """
    base_path = getattr(
        sys,
        '_MEIPASS',
        os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# Then use this function to find the asset, eg: resource("my_file")
def main():
    chatbot_app = ChatbotApp()
    chatbot_app.mainloop()

if __name__ == "__main__":
    main()

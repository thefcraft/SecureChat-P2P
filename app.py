import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
import webbrowser
import threading
import time
import sys
import datetime
import asyncio
import json, requests
import websockets
from PIL import Image
from aiortc import RTCPeerConnection, RTCSessionDescription, RTCDataChannel

from basicSymmetricKeyEncryption import BasicSymmetricKeyEncrpter
from keyShare import RSA, rsaCryptor, int_to_base255, base255_to_int
import base64, secrets

# cryptor = BasicSymmetricKeyEncrpter(key=b"None") # some secret key which is shared by rsa or so with help of maybe room code?...
def middleware(cryptor:BasicSymmetricKeyEncrpter, data: str, encrypt: bool = True):
    if encrypt: 
        data:bytes = data.encode()
        res:bytearray = cryptor.encrypt(data, update_key=True) # dynamically update the root key
        cryptor.update_key(data) # dynamically update the root key
        print(f"encrypt => {bytes(res)}")
        return base64.b64encode(res).decode() 
    else:
        data = base64.b64decode(data)
        res:bytearray = cryptor.decrypt(data, update_key=True) # dynamically update the root key
        cryptor.update_key(res) # dynamically update the root key
        print(f"decrypt => {bytes(res)}")
        return res.decode()
    
# DONE handle go back btn at wait room
# DONE add server is starting message at create room
# DONE add rsa
# DONE add loading in join room...
# DONE reset encryption on each new chat room
# DONE one client exit then handle other one alert or so..
# DONE no room message

# TODO proper exit handling...

ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("green")  # Themes: "blue" (standard), "green", "dark-blue"

class Home(ctk.CTkScrollableFrame):
    def __init__(self, master:"App", **kwargs):
        super().__init__(master, **kwargs)

        # Configure grid to expand properly
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.grid_rowconfigure(4, weight=1)
        
        # Create widgets
        self.create_widgets()
        self.root = master

    def create_widgets(self):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 0))
        header_frame.grid_columnconfigure(1, weight=1)

        logo_label = ctk.CTkLabel(header_frame, text="🛡️", font=("Arial", 24))
        logo_label.grid(row=0, column=0, padx=(0, 10))

        title_label = ctk.CTkLabel(header_frame, text="SecureChat P2P", font=("Arial", 24, "bold"))
        title_label.grid(row=0, column=1, sticky="w")

        # Navigation
        nav_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        nav_frame.grid(row=0, column=2, sticky="e")

        features_button = ctk.CTkButton(nav_frame, text="Features", command=lambda: self.scroll_to_widget(self.features_frame), fg_color="transparent", text_color="#676767", hover_color="#e0e0e0")
        features_button.grid(row=0, column=0, padx=5)

        security_button = ctk.CTkButton(nav_frame, text="Security", command=lambda: self.scroll_to_widget(self.security_frame), fg_color="transparent", text_color="#676767", hover_color="#e0e0e0")
        security_button.grid(row=0, column=1, padx=5)

        # Hero section
        hero_frame = ctk.CTkFrame(self, fg_color="transparent")
        hero_frame.grid(row=1, column=0, padx=20, pady=40, sticky="ew")
        hero_frame.grid_columnconfigure(0, weight=1)

        hero_title = ctk.CTkLabel(hero_frame, text="Secure P2P Chat", font=("Arial", 36, "bold"))
        hero_title.grid(row=0, column=0, pady=(0, 10))

        hero_subtitle = ctk.CTkLabel(hero_frame, text="Connect with others securely. Start a new chat or join an existing one with end-to-end encryption.", font=("Arial", 16), wraplength=500)
        hero_subtitle.grid(row=1, column=0, pady=(0, 20))

        button_frame = ctk.CTkFrame(hero_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0)

        start_chat_button = ctk.CTkButton(button_frame, text="Start New Chat", command=self.start_new_chat, fg_color="#4CAF50", hover_color="#45a049")
        start_chat_button.grid(row=0, column=0, padx=10)

        join_chat_button = ctk.CTkButton(button_frame, text="Join Existing Chat", command=self.join_existing_chat)
        join_chat_button.grid(row=0, column=1, padx=10)

        # Features section
        self.features_frame = ctk.CTkFrame(self, fg_color="#1c1c1c")
        self.features_frame.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        self.features_frame.grid_columnconfigure(0, weight=1)

        features_title = ctk.CTkLabel(self.features_frame, text="Key Features", font=("Arial", 24, "bold"))
        features_title.grid(row=0, column=0, pady=(20, 10))

        features = [
            ("👥 Private Chats", "Connect one-on-one in secure, private chat rooms."),
            ("🔒 End-to-End Encryption", "All messages are encrypted to ensure your privacy."),
            ("🔗 Peer-to-Peer", "Direct connections between users without intermediary servers.")
        ]
        feature_frame_c = ctk.CTkFrame(self.features_frame, fg_color="transparent")
        feature_frame_c.grid(row=0, column=0, pady=10)
        feature_frame_c.grid_columnconfigure(1, weight=1)
        for i, (feature_title, feature_desc) in enumerate(features):
            feature_frame = ctk.CTkFrame(feature_frame_c, fg_color="transparent")
            feature_frame.grid(row=i+1, column=0, pady=10, sticky="ew")
            feature_frame.grid_columnconfigure(1, weight=1)

            feature_icon = ctk.CTkLabel(feature_frame, text=feature_title.split()[0], font=("Arial", 24))
            feature_icon.grid(row=0, column=0, padx=(0, 10))

            feature_text = ctk.CTkLabel(feature_frame, text=feature_title.split(' ', 1)[1], font=("Arial", 18, "bold"))
            feature_text.grid(row=0, column=1, sticky="w")

            feature_desc_label = ctk.CTkLabel(feature_frame, text=feature_desc, font=("Arial", 14), wraplength=400)
            feature_desc_label.grid(row=1, column=1, sticky="w")

        # Security section
        self.security_frame = ctk.CTkFrame(self, fg_color="#1c1c1c")
        self.security_frame.grid(row=3, column=0, padx=20, pady=20, sticky="ew")
        self.security_frame.grid_columnconfigure(0, weight=1)

        security_title = ctk.CTkLabel(self.security_frame, text="Our Commitment to Security", font=("Arial", 24, "bold"))
        security_title.grid(row=0, column=0, pady=(20, 10))

        security_info = ctk.CTkLabel(self.security_frame, text="End-to-End Encryption: All messages are encrypted on your device and can only be decrypted by your chat partner. No one, not even us, can read your messages.\n\nNo Data Storage: We don't store any of your conversations. Once you close a chat room, all data is permanently deleted.", font=("Arial", 14), wraplength=500, justify="left")
        security_info.grid(row=1, column=0, pady=(0, 20))

        # Footer
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=20)
        footer_frame.grid_columnconfigure(1, weight=1)

        copyright_label = ctk.CTkLabel(footer_frame, text="© 2024 SecureChat P2P. All rights reserved.", font=("Arial", 12), text_color="gray")
        copyright_label.grid(row=0, column=0, sticky="w")

        terms_button = ctk.CTkButton(footer_frame, text="Terms of Service", command=lambda: self.open_link("https://github.com/thefcraft/SecureChat-P2P/"), fg_color="transparent", text_color="gray", hover_color="#e0e0e0")
        terms_button.grid(row=0, column=1, sticky="e", padx=(0, 10))

        privacy_button = ctk.CTkButton(footer_frame, text="Privacy", command=lambda: self.open_link("https://github.com/thefcraft/SecureChat-P2P/"), fg_color="transparent", text_color="gray", hover_color="#e0e0e0")
        privacy_button.grid(row=0, column=2, sticky="e")
    
    def start_new_chat(self):
        self.root.create_room()

    def join_existing_chat(self):
        room_code = ctk.CTkInputDialog(text="Enter the room code:", title="Join Existing Chat").get_input()
        if room_code:
            self.root.join_existing_room(room_code=room_code)

    def scroll_to_widget(self, widget):
        # make this a link...
        self.update_idletasks()  # Update to make sure widget positions are correct
        print(widget.winfo_y() / self.winfo_height())
        # self.yview_moveto(widget.winfo_y() / self.winfo_height())

    def open_link(self, url):
        webbrowser.open(url)

class WaitingRoom(ctk.CTkFrame):
    def __init__(self, master:"App", room_code=None, **kwargs):
        super().__init__(master, **kwargs)
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        
        # Room code (in a real app, this would be generated)
        self.room_code = room_code
        self.root = master
        self.close = False
        # Create widgets
        self.create_widgets()
        self.animate = threading.Thread(target=self.animate_waiting, daemon=True)
        self.animate.start()

    def go_back(self):
        self.destroy()
        self.root.home()
        
    def create_widgets(self):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent", height=50)
        header_frame.grid(row=0, column=0, sticky="ew", pady=(20, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = ctk.CTkLabel(header_frame, text="Waiting Room", font=("Arial", 24, "bold"))
        title_label.grid(row=0, column=0, pady=(10, 10), padx=(20, 5))
        
        end_chat_button = ctk.CTkButton(header_frame, text="Go Back", command=self.go_back, fg_color="#FF5722", hover_color="#E64A19", width=100)
        end_chat_button.grid(row=0, column=2, padx=(5, 20), pady=10)

        # Room code frame
        room_code_frame = ctk.CTkFrame(self)
        room_code_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        room_code_frame.grid_columnconfigure(0, weight=1)

        room_code_label = ctk.CTkLabel(room_code_frame, text="Your Room Code:", font=("Arial", 16))
        room_code_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.room_code_entry = ctk.CTkLabel(room_code_frame, font=("Arial", 16), text=self.room_code if self.room_code else "Loading...")
        self.room_code_entry.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        if self.room_code is None: 
            def change_loading_text():
                if self.room_code is not None: return
                elif self.room_code_entry._text == "Loading   ": self.room_code_entry.configure(text="Loading.  ")
                elif self.room_code_entry._text == "Loading.  ": self.room_code_entry.configure(text="Loading.. ")
                elif self.room_code_entry._text == "Loading.. ": self.room_code_entry.configure(text="Loading...")
                else: self.room_code_entry.configure(text="Loading   ")
                self.after(200, change_loading_text)
            self.after(200, change_loading_text)

        copy_button = ctk.CTkButton(room_code_frame, text="Copy", command=self.copy_room_code, width=60)
        copy_button.grid(row=1, column=1, padx=(0, 10), pady=5)

        # Waiting message
        self.waiting_label = ctk.CTkLabel(self, text="Waiting for your chat partner to join...", font=("Arial", 16))
        self.waiting_label.grid(row=2, column=0, pady=20)

        # Animated waiting indicator
        self.canvas = tk.Canvas(self, width=50, height=50, bg="#121212", highlightthickness=0)
        self.canvas.grid(row=3, column=0)
        self.progress = self.canvas.create_arc(10, 10, 40, 40, start=0, extent=0, fill="#4CAF50")


        # Security reminder
        security_label = ctk.CTkLabel(self, text="Your conversations are end-to-end encrypted\nand not stored on any server.", 
                                      font=("Arial", 12), text_color="gray")
        security_label.grid(row=4, column=0, pady=(0, 20))

    def set_room_code(self, room_code):
        self.room_code = room_code
        self.room_code_entry.configure(text=room_code)

    def copy_room_code(self):
        self.clipboard_clear()
        self.clipboard_append(self.room_code if self.room_code else "Loading...")
        messagebox.showinfo("Copied", "Room code copied to clipboard!")

    def animate_waiting(self):
        angle = 0
        while not self.close:
            angle = (angle + 10) % 360
            self.canvas.itemconfig(self.progress, extent=angle)
            time.sleep(0.05)

    def enter_chat(self):
        # In a real app, this would navigate to the chat room
        messagebox.showinfo("Chat Room", "Entering chat room...")
        self.quit()

    def destroy(self):
        self.close = True
        super().destroy()
        self.animate.join()
        
class ChatUIOld(ctk.CTkFrame):
    def __init__(self, master:"App", room_code, **kwargs):
        super().__init__(master, **kwargs)

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Message storage
        self.messages = []
        self.room_code = room_code
        self.root=master
        # Create widgets
        self.create_widgets()
        
        # TODO user leave ui other changes 

    def create_widgets(self):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="#4CAF50", height=50)
        header_frame.grid(row=0, column=0, sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)

        room_label = ctk.CTkLabel(header_frame, text=f"Chat Room: {self.room_code}", font=("Arial", 16, "bold"), text_color="white")
        room_label.grid(row=0, column=0, padx=10, pady=10)

        participants_label = ctk.CTkLabel(header_frame, text="Participants: 2", font=("Arial", 14), text_color="white")
        participants_label.grid(row=0, column=1, padx=10, pady=10, sticky="e")

        end_chat_button = ctk.CTkButton(header_frame, text="End Chat", command=self.end_chat, fg_color="#FF5722", hover_color="#E64A19", width=100)
        end_chat_button.grid(row=0, column=2, padx=10, pady=10)

        # Chat area
        chat_frame = ctk.CTkFrame(self)
        chat_frame.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="nsew")
        chat_frame.grid_rowconfigure(0, weight=1)
        chat_frame.grid_columnconfigure(0, weight=1)

        self.chat_display = ctk.CTkTextbox(chat_frame, font=("Arial", 14), wrap="word")
        self.chat_display.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.chat_display.configure(state="disabled")

        # Message input area
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        input_frame.grid_columnconfigure(0, weight=1)

        self.message_input = ctk.CTkEntry(input_frame, font=("Arial", 14), placeholder_text="Type your message here...")
        self.message_input.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        send_button = ctk.CTkButton(input_frame, text="Send", command=self.send_message, width=100)
        send_button.grid(row=0, column=1)

        # Bind Enter key to send message
        self.message_input.bind("<Return>", lambda event: self.send_message())

    def send_message(self):
        message = self.message_input.get().strip()
        if message:
            self.add_message("You", message)
            self.message_input.delete(0, "end")
            self.root.send_message(message)

    def add_message(self, sender, content):
        timestamp = datetime.datetime.now().strftime("%H:%M")
        formatted_message = f"[{timestamp}] {sender}: {content}\n\n"
        
        self.chat_display.configure(state="normal")
        self.chat_display.insert("end", formatted_message)
        self.chat_display.configure(state="disabled")
        self.chat_display.see("end")

        self.messages.append({"sender": sender, "content": content, "timestamp": timestamp})

    def end_chat(self):
        if messagebox.askyesno("End Chat", "Are you sure you want to end this chat? All messages will be permanently deleted."):
            # In a real app, perform cleanup operations here
            self.destroy()
            self.root.home()

class ChatUI(ctk.CTkFrame):
    def __init__(self, master:"App", room_code, **kwargs):
        super().__init__(master, **kwargs)

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.room_code = room_code
        self.root=master
        # Create widgets
        self.create_widgets()
        
        # TODO user leave ui other changes 

    def create_widgets(self):
        main_frame = ctk.CTkFrame(self, fg_color="#1c1c1c")
        main_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        # Chat header
        header_frame = ctk.CTkFrame(main_frame, fg_color="#4CAF50", corner_radius=10)
        header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        
        room_label = ctk.CTkLabel(header_frame, text=f"Chat Room: {self.room_code}", font=("Arial", 16, "bold"), text_color="white")
        room_label.grid(row=0, column=0, padx=10, pady=10)

        participants_label = ctk.CTkLabel(header_frame, text="Participants: 2", font=("Arial", 14), text_color="white")
        participants_label.grid(row=0, column=1, padx=10, pady=10, sticky="e")

        end_chat_button = ctk.CTkButton(header_frame, text="End Chat", command=self.end_chat, fg_color="#FF5722", hover_color="#E64A19", width=100)
        end_chat_button.grid(row=0, column=2, padx=10, pady=10)
        
        # Chat area
        self.chat_frame = ctk.CTkScrollableFrame(main_frame, fg_color="#1c1c1c", corner_radius=10)
        self.chat_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.chat_frame.grid_columnconfigure(0, weight=1)

        # Message input area
        input_frame = ctk.CTkFrame(main_frame, fg_color="#1c1c1c")
        input_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=(10, 5))
        input_frame.grid_columnconfigure(0, weight=1)

        self.message_input = ctk.CTkEntry(input_frame, placeholder_text="Type your message here...", height=40, font=("Arial", 14))
        self.message_input.grid(row=0, column=0, sticky="ew", padx=(0, 5))

        send_button = ctk.CTkButton(input_frame, text="Send", command=self.send_message, width=100, height=40, font=("Arial", 14))
        send_button.grid(row=0, column=1)

        # Bind Enter key to send message
        self.message_input.bind("<Return>", lambda event: self.send_message())
        
    def send_message(self):
        message = self.message_input.get().strip()
        if message:
            self.add_message("You", message)
            self.message_input.delete(0, "end")
            self.root.send_message(message)

    def add_message(self, sender, message):
        frame = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        frame.grid(sticky="ew", padx=10, pady=5)
        frame.grid_columnconfigure(0 if sender != "You" else 1, weight=1)

        bubble_color = "#DCF8C6" if sender == "You" else "#E5E5EA"
        text_color = "#000000"
        
        bubble = ctk.CTkFrame(frame, fg_color=bubble_color, corner_radius=15)
        bubble.grid(row=0, column=1 if sender == "You" else 0, sticky="e" if sender == "You" else "w")

        message_label = ctk.CTkLabel(bubble, text=message, font=("Arial", 14), text_color=text_color, wraplength=350)
        message_label.pack(padx=10, pady=5)

        time = datetime.datetime.now().strftime("%H:%M")
        time_label = ctk.CTkLabel(bubble, text=time, font=("Arial", 10), text_color="#888888")
        time_label.pack(padx=10, pady=(0, 5))
        
        # self.chat_frame.see("end") # CTkScrollableFrame
        # Scroll to the bottom
        self.chat_frame.update_idletasks()  # Ensure all widgets are updated
        self.chat_frame._parent_canvas.yview_moveto(1.0) # Scroll to the bottom (1.0 is the end of the view)

    def end_chat(self):
        if messagebox.askyesno("End Chat", "Are you sure you want to end this chat? All messages will be permanently deleted."):
            # perform cleanup operations here
            self.destroy()
            self.root.close_pc()
            # self.root.home() done at on close callback

class App(ctk.CTk):
    uri = "wss://webrtc-handshake-server.onrender.com/ws"
    endpoint = "https://webrtc-handshake-server.onrender.com"
    
    def __init__(self):
        super().__init__()
        # Configure window
        self.title("SecureChat P2P - Home")
        self.geometry("500x600")
        self.configure(fg_color="#1c1c1c")
        
        # Load the icon image (use .png or .ico files)
        # icon_image = Image.open("icon.png")  # Load your .png file

        # Convert image to PhotoImage format used by tkinter
        # icon_photo = ctk.CTkImage(image=icon_image)
        # self.iconphoto(True, icon_photo )

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Initialize 
        self.my_frame = None
        self.loop = None
        self.loop_thread = None
        self.is_running = True
        self.pc = None
        self.queue = None
        self.cryptor = None
        self.is_home = True
        self.closed_event = None
        
        
        # Create an Event object to signal completion
        self.thread_done = threading.Event()
        # self.loop.stop()  # Stop the event loop gracefully if needed
        # Signal that the thread has finished
        # self.thread_done.set()
        
    # def wait_for_thread(self):
        # Wait for the thread to finish
        # self.thread_done.wait()  # Wait until thread_done is set
        # self.loop_thread.join()  # Join the thread in the main thread
        
        self.home()
        
        # Set up custom close handler
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    def on_close(self):
        self.is_running = False
        if self.closed_event is not None: self.closed_event.set()
        
        self.destroy()  # Close the application
        
        if self.loop and self.loop.is_running():
            # self.send_message("WM_DELETE_WINDOW")
            # print("CLOSING PROCESS")
            async def run_asyncio_loop():
                await self.pc.close()
            asyncio.run_coroutine_threadsafe(run_asyncio_loop(), self.loop)
            
            self.loop.call_soon_threadsafe(self.loop.stop)
        

        if self.loop_thread and self.loop_thread.is_alive():
            print("JOINING THREAD PROCESS")
            self.loop_thread.join()

    def close_pc(self, send_message: bool = True):
        if self.pc is not None:
            self.is_running = False
            if self.loop and self.loop.is_running():
                if send_message: self.send_message("WM_DELETE_WINDOW")
                async def run_asyncio_loop():
                    await self.pc.close()
                    self.pc = None
                    self.is_running = True

                asyncio.run_coroutine_threadsafe(run_asyncio_loop(), self.loop)
                self.loop.call_soon_threadsafe(self.loop.stop)
                # self.queue_send_message = asyncio.Queue()
                self.loop = None

            if self.loop_thread and self.loop_thread.is_alive():
                self.loop_thread.join()
                self.loop_thread = None

            self.home()
        
    def home(self):
        if self.my_frame is not None: self.my_frame.destroy()
        self.is_home = True
        self.my_frame = Home(master=self)
        self.my_frame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
    
    def join_room(self, room_code):
        self.my_frame.destroy()
        
        self.is_home = False
        self.my_frame = ChatUI(master=self, room_code=room_code)
        self.my_frame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

    def send_message(self, message, use_middleware=True): 
        print(f"send message: {message}")
        if use_middleware: message = middleware(self.cryptor, message, encrypt=True)
        async def run_asyncio_loop():
            if self.queue is not None:
                await self.queue.put(message)
            else: print("queue is NONE")
        # asyncio.run(run_asyncio_loop())
        # Schedule the async function to be run on the existing event loop
        asyncio.run_coroutine_threadsafe(run_asyncio_loop(), self.loop)
    
    def start_event_loop(self, run_asyncio_loop):
            # run_asyncio_loop
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            try:
                self.loop.run_until_complete(run_asyncio_loop())
            except asyncio.exceptions.TimeoutError:
                print("Server is starting please wait...")
                messagebox.showinfo(title="Hats off to render.com", message="Handshake server is starting please wait...\nit might take 30-60 seconds.")
                self.is_home = True
                self.home()
            except RuntimeError: 
                print("Error at quiting")
            finally:
                print("SAFE QUIT")
                self.loop.stop() # Stop the event loop gracefully if needed
                self.thread_done.set()
                # self.loop_thread.join()    
    
    def create_room(self):
        self.my_frame.destroy()
        self.is_home = False
        self.my_frame = WaitingRoom(master=self, room_code=None)
        self.my_frame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
        # self.after(5000, self.my_frame.joined)
        
        
        async def run_asyncio_loop(): 
            pc = RTCPeerConnection()
            self.pc = pc
            channel = pc.createDataChannel("chat")
            # channel_log(channel, "-", "created by local party")
            closed_event = asyncio.Event()
            self.closed_event = closed_event
            queue = asyncio.Queue()
            self.queue = queue
            
            async def send_message_core():
                while True: 
                    try: 
                        message = await queue.get()
                        channel.send(message)
                    except Exception as e: 
                        closed_event.set()
                        self.task.cancel()
                    if closed_event.is_set(): break
                    
                print("Channel is no longer open. Quiting send_message_core.")
                
            # Ensure send_message_core runs concurrently
            self.task = asyncio.create_task(send_message_core())
            
            rsa = RSA()
            
            cryptor_flag = False
            is_channel_open = False
            
            @channel.on("open")
            def on_open():
                nonlocal is_channel_open
                is_channel_open = True
                channel.send(f"PUBLIC_KEY: {base64.b64encode(int_to_base255(rsa.public_key)).decode()}")
                print(f"PUBLIC_KEY: {rsa.public_key}")
                channel.send(f"PUBLIC_N: {base64.b64encode(int_to_base255(rsa.n)).decode()}")
                print(f"PUBLIC_N: {rsa.n}")
                print("Data channel is open")

            @channel.on("message")
            def on_message(message:str, use_middleware=True): 
                nonlocal cryptor_flag
                if cryptor_flag is False:
                    if message.startswith("KEY: "):
                        ske_key = message.removeprefix("KEY: ")
                        ske_key = base64.b64decode(ske_key.encode())
                        ske_key = rsa.decryptor(ske_key)
                        print(f"SKE_KEY: {ske_key}")
                        self.cryptor = BasicSymmetricKeyEncrpter(key=ske_key)
                        cryptor_flag = True
                    else: raise ValueError("something went wrong message is not KEY")
                else:
                    if use_middleware: message = middleware(self.cryptor, message, encrypt=False)
                    print(f"channel({channel.label}) < {message}")
                    self.my_frame.add_message("Peer", message)
            @channel.on("close")
            def on_close():
                print("Data channel is closed successfully...")
                # Optionally, you might want to clean up the RTCPeerConnection
                # pc.close()
                self.pc = None
                # Signal the event to stop the loop
                closed_event.set()
                self.task.cancel()
                self.queue = None
                self.close_pc(send_message=is_channel_open)
            
            # Generate an offer
            offer = await pc.createOffer()
            await pc.setLocalDescription(offer)
            print("Offer created and local description set.")
            offer_json = json.dumps({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})
            
            async with websockets.connect(self.uri) as websocket:
                await websocket.send(f"OFFER: {offer_json}")
                ID:str = str(await websocket.recv()).removeprefix("ID: ")
                print(f"Your ID : {ID}")
                if not self.is_home:
                    self.my_frame.set_room_code(ID)

                    answer = 'ALIVE: ?'
                    while answer == 'ALIVE: ?' and not self.is_home: answer:str = await websocket.recv()
                    if not self.is_home:
                        answer = answer.removeprefix("ANSWER: ")
                        data = json.loads(answer)
                        self.join_room(room_code=ID)
                if self.is_home: 
                    channel.close()
            answer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])

            await pc.setRemoteDescription(answer)
            print("Remote description set.")
            
            
            # Keep the event loop running until the event is set
            await closed_event.wait()

            if not self.is_running: return print("NOT RUNNING")
            print("SEND BACK TO HOME or EXIT")
            messagebox.showinfo(title="Peer Closed", message="The data channel has been closed.")
            self.is_home = False
            self.home()
        
        
        self.loop_thread = threading.Thread(target=lambda: self.start_event_loop(run_asyncio_loop))
        self.loop_thread.start()
    
    def join_existing_room(self, room_code):
        self.my_frame.destroy()
        
        async def run_asyncio_loop(): 
            pc = RTCPeerConnection()
            self.pc = pc #for pc.close() fn
            closed_event = asyncio.Event()
            self.closed_event = closed_event
            queue = asyncio.Queue()
            self.queue = queue
            
            
            @pc.on("datachannel")
            def on_datachannel(channel: RTCDataChannel):
                async def send_message_core():
                    while True: 
                        try: message = await queue.get()
                        except Exception as e: 
                            closed_event.set()
                            self.task.cancel()
                        if closed_event.is_set(): break
                        channel.send(message)
                    print("Channel is no longer open. Quiting send_message_core.")
                
                # Ensure send_message_core runs concurrently
                self.task = asyncio.create_task(send_message_core())
                
                print("Data channel is created")
                # channel.send("hello world!")
                
                self.my_frame = ChatUI(master=self, room_code=room_code)
                self.my_frame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
                
                PUBLIC_KEY = None
                PUBLIC_N = None
                
                @channel.on("message")
                def on_message(message:str, use_middleware=True):
                    nonlocal PUBLIC_KEY, PUBLIC_N
                    if PUBLIC_KEY is None or PUBLIC_N is None:
                        if message.startswith("PUBLIC_KEY: "):
                            key = message.removeprefix("PUBLIC_KEY: ")
                            print(f"PUBLIC_KEY: {key}")
                            PUBLIC_KEY = base255_to_int(base64.b64decode(key.encode()))
                            print(f"PUBLIC_KEY: {PUBLIC_KEY}")
                        elif message.startswith("PUBLIC_N: "):
                            n = message.removeprefix("PUBLIC_N: ")
                            print(f"PUBLIC_N: {n}")
                            PUBLIC_N = base255_to_int(base64.b64decode(n.encode()))
                            print(f"PUBLIC_N: {PUBLIC_N}")
                            ske_key = bytearray(secrets.token_bytes(64))
                            self.cryptor = BasicSymmetricKeyEncrpter(key=ske_key)
                            print(f"ske_key: {ske_key}")
                            ske_key_encrypted:str = base64.b64encode(rsaCryptor(ske_key, key=PUBLIC_KEY, n=PUBLIC_N)).decode()
                            print(f"ske_key_encrypted: {ske_key_encrypted}")
                            channel.send(f"KEY: {ske_key_encrypted}")
                        else: raise ValueError("something went wrong message is not PUBLIC_KEY or PUBLIC_N")
                    else:
                        if use_middleware: message = middleware(self.cryptor, message, encrypt=False)
                        print(f"channel({channel.label}) < {message}")
                        self.my_frame.add_message("Peer", message)
                    
                @channel.on("close")
                def on_close():
                    print("Data channel is closed successfully...")
                    self.pc = None
                    # Signal the event to stop the loop
                    closed_event.set()
                    self.task.cancel()
                    self.queue = None
                    
                    self.close_pc()
                    
            
            # Test /get-offer endpoint
            get_offer_url = f"{self.endpoint}/get-offer"
            offer_payload = {"user_id": room_code}
            response = requests.post(get_offer_url, json=offer_payload)
            offer = response.json().get("offer")
            if offer is None:
                print("No room found...")
                messagebox.showinfo("error", f"No room found...\nfor room_code: {room_code}")
                self.home()
                return
            else:
                self.my_frame.destroy()
                self.is_home = False
                self.my_frame = WaitingRoom(master=self, room_code=None)
                self.my_frame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")
            
            data = json.loads(offer)
            offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])
            
            await pc.setRemoteDescription(offer)
            print("Remote description set.")

            # Generate an answer
            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)
            print("Answer created and local description set.")

            set_answer_url = f"{self.endpoint}/set-answer"
            answer_json = json.dumps({"sdp": pc.localDescription.sdp, "type": pc.localDescription.type})
            answer_payload = {"user_id": room_code, "answer": answer_json}
            response = requests.post(set_answer_url, json=answer_payload)
            print(response.json())
            
            # Keep the event loop running until the event is set
            await closed_event.wait()
            if not self.is_running: return print("NOT RUNNING")
            messagebox.showinfo(title="Peer Closed", message="The data channel has been closed.")
            self.is_home = False
            self.home()
            
  
        
            
        self.loop_thread = threading.Thread(target=lambda:self.start_event_loop(run_asyncio_loop)) # lambda : asyncio.run(run_asyncio_loop())
        self.loop_thread.start()
        
if __name__ == "__main__":
    try:
        app = App()
        app.mainloop()
    except KeyboardInterrupt: sys.exit(0)
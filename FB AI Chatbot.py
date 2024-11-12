from fbchat import Client
from fbchat.models import *
import ssl
from getpass import getpass
import os
import logging
import sys
from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

ssl._create_default_https_context = ssl._create_unverified_context

# Define a dictionary with the available commands and their descriptions
HELP_MESSAGE = {
    "#smart": "Send a message to the bot to receive a response from OpenAI API. \n",
    "#restart ai": "Send a message to the bot to restart the AI. \n",
    "#help": "Send a message to the bot to receive a list of available commands. \n \n"
    "Note: If the bot does not respond, please send a direct message to the bot first and try again."
}

# Initialize OpenAI API credentials
client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio")

# Define a function to retrieve the response from OpenAI API
def generate_response(prompt):
    try:
        chats = client.chat.completions.create(
            model="local-model", # Adjust the model as needed for your setup
            messages=[
                {"role": "system", "content": "Answer in a consistent style."},
                {"role": "user", "content": prompt}
            ],
        )
        # Extract the message content from the completion object
        print(chats.choices[0].message)
        answer = chats.choices[0].message['content'].strip()
        return answer
    except Exception as e:
        logging.error(f"An error occurred while generating a response: {e}")
        return "I'm sorry, I wasn't able to generate a response."

# Function to restart the script
def restart_script():
    logging.info("Restarting script...")
    script_path = os.path.realpath(__file__)
    script_dir = os.path.dirname(script_path)
    os.chdir(script_dir)
    os.execv(sys.executable, ['python'] + sys.argv)


# Define the ChatBot class
class MyChatBot(Client):
     
    
    def __init__(self, email, password):
        super().__init__(email, password)

    # Function to handle incoming messages
    def onMessage(self, mid=None, author_id=None, message=None, message_object=None, thread_id=None, thread_type=ThreadType.USER, ts=None, metadata=None, msg=None, **kwargs):
        # Mark message as read
        self.markAsRead(author_id)

        # If the message is from the user and contains the keyword "*smart"
        if author_id != self.uid and "#smart" in message_object.text.lower():
            # Generate response from OpenAI API
            prompt = message_object.text.lower().replace("#smart", "Response:")
            response = generate_response(prompt)

            # If the message is in a group, reply to the message that triggered the bot
            if thread_type == ThreadType.GROUP:
                self.send(Message(text=response, reply_to_id=message_object.uid), thread_id=thread_id, thread_type=thread_type)
            # Otherwise, send the response back to the user
            else:
                self.send(Message(text=response), thread_id=thread_id, thread_type=thread_type)

        self.markAsDelivered(author_id, thread_id)

        # If the user sends the message "#restart ai"
        if author_id != self.uid and "#restart ai" in message_object.text.lower():
            # Send a message to the user indicating that the script will be restarted
            self.send(Message(text="Restarting the Bot..."), thread_id=thread_id, thread_type=thread_type)
            
            # Call the restart function to restart the script
            restart_script()

        self.markAsDelivered(author_id, thread_id)
        
        # If the message is from a group
        if thread_type == ThreadType.GROUP:
            # If the message mentions the bot
            if f"@{self.uid}" in message_object.text:
                # Generate response from OpenAI API
                prompt = message_object.text.lower().replace(f"@{self.uid}", "Response:")
                response = generate_response(prompt)
                
                # Reply to the message that mentioned the bot
                self.send(Message(text=response, reply_to_id=message_object.uid), thread_id=thread_id, thread_type=thread_type)

        self.markAsDelivered(author_id, thread_id)
        
        # If the message is from the user and contains the keyword "#help"
        if author_id != self.uid and "#help" in message_object.text.lower():
            # Send a message to the user with the available commands
            help_message = "Available commands:\n" + "\n".join([f"{key}: {value}" for key, value in HELP_MESSAGE.items()])
            self.send(Message(text=help_message), thread_id=thread_id, thread_type=thread_type)

        self.markAsDelivered(author_id, thread_id)


#Facebook account        
email = "" #email of your fb account
password = "\" #password of your fb account
client = MyChatBot(email, password)
client.listen()
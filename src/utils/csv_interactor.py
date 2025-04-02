import pandas as pd
import os
import time

import pandas as pd
import os

class ConversationLogXLSX:
    def __init__(self, xlsx_name='conversation_log.xlsx'):
        """Initialize the ConversationLog with the specified XLSX file.
        
        Args:
            file_name (str): The name of the XLSX file to use for logging.
        """
        self.file_name = xlsx_name

        # Create the file if it doesn't exist
        if not os.path.exists(self.file_name):
            self.create_xlsx_log_file()

    def create_xlsx_log_file(self):
        """Create a new XLSX log file with headers."""
        df = pd.DataFrame(columns=["Participant", "Dialogue"])
        df.to_excel(self.file_name, index=False)

    def add_interviewer_message_to_xlsx(self, message: str):
        """Add a new message from the interviewer to the conversation log.
        
        Args:
            message (str): The content of the interviewer's message.
        """
        # Read existing data
        df = self.get_xlsx_conversation()
        # Create a new entry
        new_entry = pd.DataFrame({"Participant": ["Interviewer"], "Dialogue": [message]})
        # Append new entry
        df = pd.concat([df, new_entry], ignore_index=True)
        # Write back to Excel
        df.to_excel(self.file_name, index=False)

    def add_candidate_message_to_xlsx(self, message: str):
        """Add a new message from the candidate to the conversation log.
        
        Args:
            message (str): The content of the candidate's message.
        """
        # Read existing data
        df = self.get_xlsx_conversation()
        # Create a new entry
        new_entry = pd.DataFrame({"Candidate": [""], "Dialogue": [message]})
        # Append new entry
        df = pd.concat([df, new_entry], ignore_index=True)
        # Write back to Excel
        df.to_excel(self.file_name, index=False)

    def get_xlsx_conversation(self):
        """Retrieve all messages from the conversation log.
        
        Returns:
            DataFrame: A DataFrame containing all messages in the conversation log.
        """
        return pd.read_excel(self.file_name)
    
    def clear_xlsx_log(self):
        """Clear all messages from the conversation log."""
        self.create_log_file()  # Recreate the log file

    def get_last_message_from_xlsx(self):
        """Retrieve the last message from the conversation log.
        
        Returns:
            dict: The last message as a dictionary or None if no messages exist.
        """
        df = self.get_xlsx_conversation()
        if not df.empty:
            return df.iloc[-1].to_dict()
        return None
    
    def get_xlsx_message_count(self):
        """Get the total number of messages in the conversation log.
        
        Returns:
            int: The number of messages in the conversation log.
        """
        df = self.get_xlsx_conversation()
        return len(df)

    def print_xlsx_conversation_log(self):
        """Print all messages in a readable format."""
        df = self.get_xlsx_conversation()
        for index, row in df.iterrows():
            interviewer_msg = row['Interviewer']
            candidate_msg = row['Candidate']
            if interviewer_msg:
                print(f"Interviewer: {interviewer_msg}")
            if candidate_msg:
                print(f"Candidate: {candidate_msg}")

    def detect_file_changes_in_xlsx(self, last_modified_time):
        """Check if the XLSX file has been modified."""
        current_modified_time = os.path.getmtime(self.file_name)
        if current_modified_time != last_modified_time:
            print("File XLSX has changed!")
            return current_modified_time
        return last_modified_time


class ConversationLogCSV:
    def __init__(self, csv_fname='conversation_log.csv'):
        """Initialize the ConversationLog with the specified CSV file.
        
        Args:
            file_name (str): The name of the CSV file to use for logging.
        """
        self.csv_fname = csv_fname

        # Create the file if it doesn't exist
        if not os.path.exists(self.csv_fname):
            self.create_csv_log_file()   
            
    def create_csv_log_file(self):
        """Create a new CSV log file with headers."""
        # df = pd.DataFrame(columns=["Participant", "Dialogue"])
        df = pd.DataFrame(columns=["Dialogue"])
        df.to_csv(self.csv_fname, index=False)
        
    def add_interviewer_message_to_csv(self, message: str):
        """Add a new message from the interviewer to the conversation log.
        
        Args:
            message (str): The content of the interviewer's message.
        """
        # Create a new entry
        new_entry = pd.DataFrame({"Dialogue": [message]})
        # Append new entry to CSV
        new_entry.to_csv(self.csv_fname, index=False, header=False, mode='a')

    def add_candidate_message_to_csv(self, message: str):
        """Add a new message from the candidate to the conversation log.
        
        Args:
            message (str): The content of the candidate's message.
        """
        # Create a new entry
        new_entry = pd.DataFrame({"Dialogue": [message]})
        # Append new entry to CSV
        new_entry.to_csv(self.csv_fname, index=False, header=False, mode='a')

    def get_csv_conversation(self):
        """Retrieve all messages from the conversation log.
        
        Returns:
            DataFrame: A DataFrame containing all messages in the conversation log.
        """
        return pd.read_csv(self.csv_fname)

    def clear_csv_log(self):
        """Clear all messages from the conversation log."""
        self.create_log_file()  # Recreate the log file

   
    def get_last_message_from_csv(self):
        """Retrieve the last message from the conversation log.
        
        Returns:
            dict: The last message as a dictionary or None if no messages exist.
        """
        df = self.get_csv_conversation()
        if not df.empty:
            return df.iloc[-1].to_dict()
        return None
    
    def get_csv_message_count(self):
        """Get the total number of messages in the conversation log.
        
        Returns:
            int: The number of messages in the conversation log.
        """
        df = self.get_conversation()
        return len(df)

    # def print_csv_conversation_log(self):
    #     """Print all messages in a readable format."""
    #     df = self.get_csv_conversation()
    #     for index, row in df.iterrows():
    #         interviewer_msg = row['Interviewer']
    #         candidate_msg = row['Candidate']
    #         if interviewer_msg:
    #             print(f"Interviewer: {interviewer_msg}")
    #         if candidate_msg:
    #             print(f"Candidate: {candidate_msg}")

    def print_csv_conversation_log(self):
        """Print all messages in a readable format."""
        df = self.get_csv_conversation()
        for index, row in df.iterrows():
            msg = row['Dialogue']
            if msg:
                print(f"{msg}")
    
    def detect_file_changes_in_csv(self, last_modified_time):
        """Check if the CSV file has been modified."""
        current_modified_time = os.path.getmtime(self.csv_fname)
        if current_modified_time != last_modified_time:
            print("File CSV has changed!")
            return current_modified_time
        return last_modified_time

# Example usage
def main():
    conversation_log = ConversationLogCSV()
    
    # Initialize last modified time
    last_modified_time = os.path.getmtime(conversation_log.csv_fname) if os.path.exists(conversation_log.csv_fname) else 0

    conversation_log.add_interviewer_message_to_csv("Hello, can you tell me about yourself?")
    # Polling for file changes
    while True:
        # Check for changes in the file
        last_modified_time = conversation_log.detect_file_changes_in_csv(last_modified_time)

        # Read the updated file if it has changed
        if last_modified_time != os.path.getmtime(conversation_log.csv_fname):
            df = conversation_log.get_csv_conversation()
            print("\nUpdated contents of the file:")
            print(":"+df+":")
            if str(df).endswith("\n"):
                conversation_log.add_interviewer_message_to_csv("Please continue with more ...")
            else:
                conversation_log.add_interviewer_message_to_csv("\nPlease continue with more ...")   

    ######################################

    # conversation_log = ConversationLogCSV()
    
    # # Initialize last modified time
    # last_modified_time = os.path.getmtime(conversation_log.csv_fname) if os.path.exists(conversation_log.csv_fname) else 0

    # conversation_log.add_interviewer_message_to_csv("Hello, can you tell me about yourself?")
    # # Polling for file changes
    # while True:
    #     # Check for changes in the file
    #     last_modified_time = conversation_log.detect_file_changes_in_csv(last_modified_time)

    #     # Read the updated file if it has changed
    #     if last_modified_time != os.path.getmtime(conversation_log.csv_fname):
    #         df = conversation_log.get_csv_conversation()
    #         print("\nUpdated contents of the file:")
    #         print(":"+df+":")
    #         if str(df).endswith("\n"):
    #             conversation_log.add_interviewer_message_to_csv("Please continue with more ...")
    #         else:
    #             conversation_log.add_interviewer_message_to_csv("\nPlease continue with more ...") 


if __name__ == "__main__":
    main()

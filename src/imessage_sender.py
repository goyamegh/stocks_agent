import subprocess

def send_imessage(message, phone_number):
    """
    Sends an iMessage via AppleScript using the macOS Messages app.
    
    Parameters:
      - message: The message to send.
      - phone_number: The recipient's phone number in international format (e.g., "+12345678900").
      
    Returns:
      True if the message was sent, False otherwise.
      
    Note: This function works only on macOS and if your iMessage is properly configured.
    """
    apple_script = f'''
    tell application "Messages"
        set targetService to 1st service whose service type = iMessage
        set targetBuddy to buddy "{phone_number}" of targetService
        send "{message}" to targetBuddy
    end tell
    '''
    process = subprocess.Popen(
        ["osascript", "-"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout, stderr = process.communicate(apple_script.encode('utf-8'))
    if stderr:
        print("Error sending iMessage:", stderr.decode('utf-8'))
        return False
    return True

if __name__ == "__main__":
    phone_number = "+12345678900"
    message = "Test message from Python via iMessage!"
    if send_imessage(message, phone_number):
        print("Message sent successfully.")
    else:
        print("Failed to send message.") 
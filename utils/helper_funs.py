import os
import datetime

# Save history into markdown file with timestamps
def save_conv_history(conv_history, path='conv_history'):
    if not os.path.exists(path):
        os.makedirs(path)
    
    current_dt = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    file_path = os.path.join(path, f'{current_dt}.md')

    # TODO: Check format
    with open(file_path, 'w') as f:
        for message in conv_history:
            # TODO: Better name than system?
            if message["role"] in ["user", "system"]:
                message_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                role_title = "User" if message["role"] == "user" else "System"
                f.write(f"{message_time} **{role_title} {message['role'].title()}:** {message['content']}\\n\\n")
    return file_path

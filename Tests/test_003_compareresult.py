import pandas as pd
import os
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
folder_location = project_root / "logs" #logs folder in project root

receiver_file = folder_location / "received_messages.ndjson"
sender_file = folder_location / "sent_messages.ndjson"

df_receiver = pd.read_json(receiver_file, lines=True)
df_sender = pd.read_json(sender_file, lines=True)


def compare_messages(df_receiver, df_sender):
    """Compare messages from receiver and sender"""
    sender_messages = df_sender['message'].tolist()
    receiver_messages = df_receiver['message'].tolist()

    len_sender = len(sender_messages)
    len_receiver = len(receiver_messages)

    if(len_sender != len_receiver):
        loss_count = abs(len_sender - len_receiver)
        print(f"{loss_count} messages lost during transmission.")
    else:
        print("No messages lost during transmission.")

    min_length = min(len_sender, len_receiver)
    mismatch_count = 0
    for i in range(min_length):
        if sender_messages[i] != receiver_messages[i]:
            mismatch_count += 1
            print(f"Mismatch at index {i}: Sent '{sender_messages[i]}', Received '{receiver_messages[i]}'")

    if mismatch_count > 0:
        print(f"{mismatch_count} message(s) mismatched.")
    else:
        print("All messages matched successfully.")

if __name__ == "__main__":
    compare_messages(df_receiver, df_sender)
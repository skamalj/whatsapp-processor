import json
from utils import extract_whatsapp_messages, extract_recipient
import os
import boto3

def lambda_handler(event, context):
    
    for record in event["Records"]:
        body = json.loads(record["body"])  # SQS message body
        if body.get('object') == 'whatsapp_business_account':
            # Ignore delivery status updates
            changes = body.get("entry", [])[0].get("changes", [])
            for change in changes:
                value = change.get("value", {})
                if "statuses" in value:  # If it's a delivery status, ignore it
                    print("Received delivery status update, ignoring...")
                    return
            message = extract_whatsapp_messages(body)
            recipeint = extract_recipient(body)
            print(f"Message recieved from {recipeint}:  {message}")
            input_message = {
                "channel_type": "whatsapp",
                "from": recipeint,
                "messages": message
            }
            sqs_queue_url = os.environ["UNIFIED_QUEUE_URL"]
            sqs_client = boto3.client("sqs")
            message_body = json.dumps(input_message)
            sqs_response = sqs_client.send_message(
                QueueUrl=sqs_queue_url,
                MessageBody=message_body
            )
            print(sqs_response)
        else:
            print(f"Ignoring: Message: NOT from WhatsApp: {body}")
    return


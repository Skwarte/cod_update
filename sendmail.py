from twilio.rest import Client

# Your Account SID from twilio.com/console
account_sid = "AC5381473413333239de1f629a23c5c874"
# Your Auth Token from twilio.com/console
auth_token  = "ec277c55e0b92c8bcf30fc2457151b71"

client = Client(account_sid, auth_token)

message = client.messages.create(
    to="+17735108759", 
    from_="+18606070114",
    body="Hello from Python!")

print(message.sid)


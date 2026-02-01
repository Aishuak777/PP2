command = "start"

if command == "start":
    action = "Starting"
elif command == "stop":
    action = "Stopping"
elif command == "pause":
    action = "Pausing"
else:
    action = "Unknown command"

print(action)

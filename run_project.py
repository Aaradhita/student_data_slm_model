import subprocess
import sys
import time

print("Starting Stage 3 API...")
subprocess.Popen([sys.executable, "stage3_api.py"])

time.sleep(2)  # give Stage 3 time to start

print("Starting Stage 5 Chatbot...")
subprocess.Popen([sys.executable, "stage5_chat_api.py"])

print("\n✅ Project is running")
print("👉 Open browser and go to:")
print("   http://127.0.0.1:9000\n")

input("Press ENTER to stop all servers...")

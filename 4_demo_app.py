"""STEP 4 - starts the hold-to-talk demo page and opens it in your browser. Use it to record the 2-minute demo."""
import threading, webbrowser
import demo_app

threading.Timer(1.2, lambda: webbrowser.open("http://localhost:7860")).start()
print("Demo running at http://localhost:7860  (stop with the red square in VS Code)")
demo_app.app.run(host="127.0.0.1", port=7860)

from backend.app.ai.gemini import ask_gemini


result = ask_gemini(
    "Explain a car marketplace in one simple sentence."
)


print(result)
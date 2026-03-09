# ================= Test  =================
if __name__ == "__main__":
    from config import get_api_key
    from llm_interface import AihubmixClient

    # Initialization
    aihubmix_client = AihubmixClient(get_api_key())

    test_messages = [{"role": "user", "content": "Hello, please introduce yourself."}]

    # 1. Call GPT 5 nano
    print("--- GPT 5 nano Response ---")
    print(aihubmix_client.chat_completion("gpt-5-nano", test_messages))

    # 2. Call Claude 3 Haiku
    print("\n--- Claude 3 Haiku Response---")
    print(aihubmix_client.chat_completion("claude-3-haiku-20240307", test_messages))

    # 3. Call Gemini 2 Flash Lite
    print("\n--- Gemini 2 Flash Lite Response ---")
    print(aihubmix_client.chat_completion("gemini-2.0-flash-lite", test_messages))
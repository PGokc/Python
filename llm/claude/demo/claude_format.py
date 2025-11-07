import os

import anthropic


def chat_with_claude(api_key, message, base_url=None):
    client = anthropic.Anthropic(
        api_key=api_key,
        base_url=base_url
    )

    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[{"role": "user", "content": message}]
        )
        return response.content
    except Exception as e:
        print(f"错误: {str(e)}")
        raise


if __name__ == "__main__":
    api_key = os.getenv("GPTSAPI_API_KEY")
    print(api_key)
    base_url = "https://api.gptsapi.net"
    print(chat_with_claude(api_key, "你好", base_url))
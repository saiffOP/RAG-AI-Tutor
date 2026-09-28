import tiktoken


_encoding = tiktoken.get_encoding("cl100k_base")


def encode(text: str) -> list[int]:
    return _encoding.encode(text)


def decode(tokens: list[int]) -> str:
    return _encoding.decode(tokens)


def count_tokens(text: str) -> int:
    return len(encode(text))
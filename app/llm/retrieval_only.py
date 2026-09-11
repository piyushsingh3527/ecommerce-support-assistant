def answer_from_context(question: str, context: str) -> str:
    if not context.strip():
        return "I could not find this information in the knowledge base."

    return (
        "I found the following information in the knowledge base:\n\n"
        + context
    )
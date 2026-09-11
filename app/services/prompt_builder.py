def build_context(results: list[dict]) -> str:
    context_parts = []

    for result in results:
        context_parts.append(
            f"Source: {result['source']}\n"
            f"Content: {result['content']}"
        )

    return "\n\n".join(context_parts)
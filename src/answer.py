from dotenv import load_dotenv
from openai import OpenAI

from config import CHAT_MODEL, MAX_DISTANCE, RELATIVE_MARGIN
from retrieve import retrieve

load_dotenv()
client = OpenAI()

SYSTEM_PROMPT = (
    "You are an IT support assistant. Answer ONLY using the provided context. "
    "If the context does not contain the answer, say you do not know. "
    "Be concise and give steps as a numbered list. Do not invent details."
)


def answer(question):
    hits = retrieve(question)
    for h in hits:  # debug output, useful for tuning MAX_DISTANCE
        print(f"  [debug] {h['source']}  distance={h['distance']:.3f}")

    relevant = [h for h in hits if h["distance"] <= MAX_DISTANCE]
    if not relevant:
        return "I could not find this in the knowledge base.", []
    best = min(h["distance"] for h in relevant)
    relevant = [h for h in relevant if h["distance"] <= best + RELATIVE_MARGIN]

    context = "\n\n".join(f"[{h['source']}]\n{h['text']}" for h in relevant)
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {question}"},
        ],
    )
    text = response.choices[0].message.content
    if text.strip().lower().startswith("i do not know"):
        return text, []
    sources = sorted({h["source"] for h in relevant})
    return text, sources


if __name__ == "__main__":
    while True:
        question = input("\nQuestion (or 'q' to quit): ").strip()
        if question.lower() == "q":
            break
        text, sources = answer(question)
        print("\n" + text)
        if sources:
            print("\nSources: " + ", ".join(sources))
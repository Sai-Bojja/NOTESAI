from sentence_transformers import SentenceTransformer
import chromadb
import openai
import os

# Set your OpenAI API key securely
openai.api_key = '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'

# Load models and vector store
model = SentenceTransformer('all-MiniLM-L6-v2')
chroma_client = chromadb.Client()
collection = chroma_client.get_or_create_collection("notesai")

# Embed and store notes
def embed_note_and_store(note_id, title, content):
    full_text = f"{title}\n{content}"
    embedding = model.encode(full_text).tolist()
    collection.add(documents=[full_text], embeddings=[embedding], ids=[str(note_id)])
    print(f"*** EMBEDDING AND STORING NOTE ID: {note_id} ***")
    print(f"Stored note {note_id}: {full_text}")

# Retrieve relevant notes
def retrieve_relevant_notes(query, n_results=8):
    embedding = model.encode(query).tolist()
    results = collection.query(query_embeddings=[embedding], n_results=n_results)
    top_matches = results['documents'][0] if results['documents'] else []
    print(f"Retrieved relevant notes: {top_matches}")
    return top_matches

# Use OpenAI to synthesize answers from retrieved notes
def rag_query(query):
    top_matches = retrieve_relevant_notes(query)

    if not top_matches:
        return "I couldn't find any relevant notes to answer your question."

    # Concatenate matched notes to form context
    context = "\n\n".join(top_matches)
    prompt = (
        f"Answer the following question only using the context below.\n"
        f"If the answer is not in the context, say 'I don't know based on the provided notes.'\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}\n"
        f"Answer:"
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-4",  # Ensure this model is accessible to your API key
            messages=[
                {"role": "system", "content": "You are an assistant who only answers based on the provided notes. If the answer isn't in the notes, respond with 'I don't know based on the provided notes'."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except openai.error.OpenAIError as e:
        print(f"An OpenAI error occurred: {e}")
        return "An error occurred while trying to answer your question."

if __name__ == '__main__':
    pass # Keeping this empty as the primary interaction is through Flask
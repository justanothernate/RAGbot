from docx import Document
import pandas as pd
import openai

doc_to_parse = "test.docx"
embeddings_file = "test.csv"

def num_tokens(text: str) -> int:
    return len(text.split())


def split_strings_from_subsection(subsection: str, max_tokens: int = 1000, max_recursion: int = 5) -> list[str]:
    num_tokens_in_string = num_tokens(subsection)
    if num_tokens_in_string <= max_tokens:
        return [subsection]
    elif max_recursion == 0:
        return [subsection[:max_tokens]]
    else:
        for delimiter in ["\n\n", "\n", ". "]:
            left, right = subsection.split(delimiter, 1)
            if left == "" or right == "":
                continue
            else:
                results = []
                for half in [left, right]:
                    half_strings = split_strings_from_subsection(half, max_tokens=max_tokens, max_recursion=max_recursion - 1)
                    results.extend(half_strings)
                return results
    return [subsection[:max_tokens]]

def read_docx(file_path):
    doc = Document(file_path)
    current_section = []
    all_sections = []

    # Split the document into sections based on the "Heading 1" style
    for para in doc.paragraphs:
        if para.style.name == 'Heading 1':
            if current_section:
                all_sections.append("\n".join(current_section))
                current_section = []
            current_section.append(para.text)
        else:
            current_section.append(para.text)

    if current_section:
        all_sections.append("\n".join(current_section))

    MAX_TOKENS = 1000
    parsed_strings = []
    for section in all_sections:
        parsed_strings.extend(split_strings_from_subsection(section, max_tokens=MAX_TOKENS))

    print(f"{len(all_sections)} sections split into {len(parsed_strings)} strings.")
    return parsed_strings

if __name__ == "__main__":
    parsed_strings = read_docx(doc_to_parse)

    EMBEDDING_MODEL = "text-embedding-ada-002"
    BATCH_SIZE = 1000

    # Create the embeddings from the parsed strings
    embeddings = []
    for batch_start in range(0, len(parsed_strings), BATCH_SIZE):
        batch_end = batch_start + BATCH_SIZE
        batch = parsed_strings[batch_start:batch_end]
        print(f"Batch {batch_start} to {batch_end-1}")
        response = openai.embeddings.create(model=EMBEDDING_MODEL, input=batch)
        for i, be in enumerate(response.data):
            assert i == be.index
        batch_embeddings = [e.embedding for e in response.data]
        embeddings.extend(batch_embeddings)

    df = pd.DataFrame({"text": parsed_strings, "embedding": embeddings})

    SAVE_PATH = embeddings_file

    df.to_csv(SAVE_PATH, index=False)
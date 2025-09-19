"""
TODO: Implement web content extraction using LangChain WebBaseLoader

Requirements:
1. Use WebBaseLoader to extract content from web pages
2. Clean and preprocess the extracted text
3. Implement text chunking with overlap
4. Save processed chunks with metadata
5. Handle edge cases (empty content, large documents)

Example usage:
    python extract_content.py --url https://example.com
"""

import os
import argparse
from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
import re
import json
load_dotenv()

def clean_text(text: str) -> str:
    """
    Cleans the extracted text by removing extra whitespace and non-printable characters.

    Args:
        text (str): The text to clean.

    Returns:
        str: The cleaned text.
    """
    # Replace multiple newlines/spaces with a single one
    text = re.sub(r'\s+', ' ', text)
    # Remove non-printable characters
    text = "".join(filter(lambda x: x.isprintable(), text))
    return text.strip()

def extract_content_from_url(url: str):
    """
    Extracts content from a given URL using WebBaseLoader.

    Args:
        url (str): Website URL to extract content from.

    Returns:
        list: A list of Document objects, or an empty list if extraction fails.
    """
    try:
        print(f"Loading documents from the {url}...")
        loader = WebBaseLoader([url])
        docs = loader.load()
        # Handle edge case: empty content
        if not docs or not docs[0].page_content.strip():
            print(f"No content found at {url}. Skipping.")
            return []

        # Clean and preprocess the extracted text
        for doc in docs:
            doc.page_content = clean_text(doc.page_content)

        return docs
    except Exception as e:
        print(f"ERROR: Failed to extract content from {url}. Reason: {e}")
        return []


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200):
    """
    Splits a given text into smaller chunks with a specified overlap.

    Args:
        text (str): Text to chunk.
        chunk_size (int): Size of each chunk.
        overlap (int): Overlap between chunks.

    Returns:
        list: A list of text chunks.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=len,
    )
    chunks = text_splitter.split_text(text)
    print(f"INFO: Split text into {len(chunks)} chunks.")
    return chunks

def get_last_chunk_number(directory: str) -> int:
    """
    Calculates the last chunk number by inspecting filenames in the output directory.

    Args:
        directory (str): The directory where chunks are stored.

    Returns:
        int: The highest chunk number found, or 0 if the directory is empty or doesn't exist.
    """
    if not os.path.isdir(directory):
        return 0
    
    last_num = 0
    for filename in os.listdir(directory):
        if filename.startswith("chunk_") and filename.endswith(".json"):
            try:
                # Extract number from filename like 'chunk_123.json'
                num = int(filename.split('_')[1].split('.')[0])
                if num > last_num:
                    last_num = num
            except (ValueError, IndexError):
                # Ignore files that don't match the expected format
                continue
    return last_num


def save_chunks(chunks: list, output_dir: str = "data/extracted_content"):
    """
    Saves processed chunks to individual JSON files. The filename is derived
    from the 'chunk_number' in the document's metadata.

    Args:
        chunks (list): List of Document objects to save.
        output_dir (str): Directory to save chunks.
    """
    if not chunks:
        print("INFO: No chunks to save.")
        return

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    print(f"INFO: Saving {len(chunks)} chunks to '{output_dir}'...")

    for i, chunk in enumerate(chunks):
        # Construct a dictionary to hold both content and metadata
        chunk_data = {
            "page_content": chunk.page_content,
            "metadata": chunk.metadata
        }
        
        # Determine filename from metadata to ensure continuity
        chunk_number = chunk.metadata.get('chunk_number')
        if chunk_number is None:
            print(f"WARNING: Chunk {i} is missing 'chunk_number' metadata. Skipping.")
            continue

        # Define the output file path
        file_path = os.path.join(output_dir, f"chunk_{chunk_number}.json")

        # Write the dictionary to a JSON file
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(chunk_data, f, ensure_ascii=False, indent=4)

    print("INFO: Successfully saved all chunks.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract content from web pages")
    parser.add_argument("--url", required=False, help="URL to extract content from")
    parser.add_argument("--output", default="data/extracted_content", help="Output directory for chunks")
    
    args = parser.parse_args()
    
    url = args.url or os.getenv("TARGET_URL")
    if not url:
        print("ERROR: No URL provided. Please use the --url argument or set the TARGET_URL environment variable.")
    else:
        print(f"--- Starting content extraction from {url} ---")

        # 1. Extract content from the URL
        extracted_docs = extract_content_from_url(url)

        if extracted_docs:
            all_chunked_docs = []
            
            # Determine the starting chunk number based on existing files
            last_chunk_number = get_last_chunk_number(args.output)
            if last_chunk_number > 0:
                print(f"INFO: Found {last_chunk_number} existing chunks. New chunks will be added.")

            # 2. Process each document individually
            print("INFO: Processing and chunking extracted documents...")
            for doc in extracted_docs:
                # Get the raw text and original metadata from the document
                raw_text = doc.page_content
                original_metadata = doc.metadata

                # Use the chunk_text function on the raw text
                text_chunks = chunk_text(raw_text)
                
                # 3. Re-create Document objects for each chunk with updated metadata
                for i, chunk_str in enumerate(text_chunks):
                    # Create a copy of the metadata to avoid modifying the original
                    chunk_metadata = original_metadata.copy()
                    
                    # Increment chunk number from the last one found
                    chunk_metadata['chunk_number'] = last_chunk_number + i + 1
                    
                    new_doc = Document(
                        page_content=chunk_str,
                        metadata=chunk_metadata
                    )
                    all_chunked_docs.append(new_doc)
            
            # 4. Save the final list of processed chunks
            save_chunks(all_chunked_docs, args.output)
            print(f"--- Execution finished: Successfully processed and saved content from {url} ---")
        else:
            print(f"--- Execution finished: No new content was processed from {url} ---")

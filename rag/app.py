from langchain_google_genai import ChatGoogleGenerativeAI

from document_loader import load_documents_into_database
import argparse
import sys
from dotenv import load_dotenv

load_dotenv()
import os

from llm import getChatChain


def main(llm_model_name: str, embedding_model_name: str, documents_path: str) -> None:
    # Ensure Google API key is provided
    if not os.getenv("GOOGLE_API_KEY"):
        print("GOOGLE_API_KEY environment variable is not set. Please export your key before running.")
        sys.exit(1)

    # Creating database form documents
    try:
        db = load_documents_into_database(embedding_model_name, documents_path)
    except FileNotFoundError as e:
        print(e)
        sys.exit()

    llm = ChatGoogleGenerativeAI(model=llm_model_name)
    chat = getChatChain(llm, db)

    while True:
        try:
            user_input = input(
                "\n\nPlease enter your question (or type 'exit' to end): "
            ).strip()
            if user_input.lower() == "exit":
                break
            else:
                chat(user_input)
        
        except KeyboardInterrupt:
            break


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run RAG with Google Gemini via LangChain.")
    parser.add_argument(
        "-m",
        "--model",
        default="gemini-pro",
        help="The name of the LLM model to use.",
    )
    parser.add_argument(
        "-e",
        "--embedding_model",
        default="models/embedding-001",
        help="The name of the embedding model to use.",
    )
    parser.add_argument(
        "-p",
        "--path",
        default="Research",
        help="The path to the directory containing documents to load.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    main(args.model, args.embedding_model, args.path)
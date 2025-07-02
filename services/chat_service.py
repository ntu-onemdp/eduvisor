from langchain_openai import OpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.callbacks import get_openai_callback
from langchain_openai import ChatOpenAI
import os
from services.logger import Logger
from models.vector_store import VectorStore

logger = Logger()


class ChatService:
    def __init__(self, vector_store: VectorStore):
        OpenAI.api_key = os.getenv("OPENAI_API_KEY")
        if not OpenAI.api_key:
            raise ValueError(
                "OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable."
            )
        self.vector_store = vector_store.vector_store
        self.llm = self._initialize_llm()

    # 4o is a good model as well
    def _initialize_llm(self, model="gpt-4o-mini", temperature=0.6):
        """Function to initialize LLM"""
        llm = ChatOpenAI(model=model, max_tokens=800, temperature=temperature)

        logger.info(f"LLM initialized with model: {model}, temperature: {temperature}")
        return llm

    def query_vectorstore(self, query, k=5):
        """Function to query vector store"""
        results = self.vector_store.similarity_search_with_score(query, k=k)
        # Return the context along with metadata
        context_with_metadata = []
        for doc, _ in results:
            # Extract content, title, and page number from metadata
            title = doc.metadata.get("title", "Unknown Title")
            page = doc.metadata.get("page", "Unknown Page")
            context_with_metadata.append(
                {
                    "content": doc.page_content,
                    "title": title,
                    "page": page,
                }
            )
        return context_with_metadata

    def format_contexts(self, contexts):
        final_contexts = []

        for context in contexts:
            title = context.get("title", "Untitled")
            page = context.get("page", "Unknown")
            content = context.get("content", "")
            context_str = f"Slide Title: {title}, Slide Page: {page}\n{content}\n"
            final_contexts.append(context_str)

        return "".join(final_contexts)

    def invoke_response(self, persona, task, conditions, output_style, query):
        """
        Generates a response from the LLM using the given persona, task, and context from a vectorstore. Builds persona of gpt.

        Args:
            llm: The language model instance.
            persona (str): Persona description for the assistant.
            task (str): The task or topic scope.
            conditions (str): Additional conditions or constraints.
            output_style (str): Desired output style for the response.
            query (str): The user's query.

        Returns:
            tuple: Clean response, tokens used, and main topic (if available).
        """

        # Construct initial system message
        sysmsg = f"{persona} {task} {conditions} {output_style}"
        conversation = [SystemMessage(content=sysmsg)]

        # Retrieve context from vectorstore
        raw_contexts = self.query_vectorstore(query, k=5)
        if not raw_contexts:
            return "No relevant context found.", 0, None
        trimmed_contexts = self.format_contexts(raw_contexts)

        # determine the main topic
        maintopic = raw_contexts[0].get("title", None) if raw_contexts else None

        # build the query with the trimmed context
        context_query = f"""

        Answer query based on context provided.\n
        Context: \n {trimmed_contexts}
        Query: {query}  

        Response Formatting Guidelines:
        - Use paragraphs to separate key ideas.
        - Be as concise as possible and answer the question to the best of your ability.
        - If the query is within the course scope, include the slide title and page used in brackets at the end of the whole response.
        """
        logger.debug(context_query)
        conversation.append(HumanMessage(content=context_query))

        # generate response from the LLM
        response, tokens_used = self.get_tokens_used(conversation)

        # clean up the response
        clean_response = (
            response.replace("System:", "")
            .replace("Human:", "")
            .replace("Answer:", "")
            .strip()
        )

        return clean_response, tokens_used, maintopic

    def get_tokens_used(self, conversation):
        """Function to check API usage"""
        with get_openai_callback() as cb:
            response = self.llm.invoke(conversation)
            tokens_used = cb.total_tokens  # get total tokens used in this query
        return response.content, tokens_used

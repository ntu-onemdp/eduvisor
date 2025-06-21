
from models.vectorstore_model import *
from services.chat_service import ChatService
import pandas as pd
import csv
from langchain_core.messages import HumanMessage, SystemMessage
import tiktoken

def init_judge(chat_service):
    llm = chat_service.initialize_llm(model="gpt-4o", temperature="0.0")
    return llm

def init_vta(chat_service):
    llm = chat_service.initialize_llm(model="gpt-4o-mini")
    course_id = 'SC2107'

    vector_store_response = load_vectorstore_from_gcs(course_id)

    if vector_store_response["code"] == 200:  
        loaded_faiss_vs = vector_store_response["data"]
    else: 
        raise Exception('failed to load faiss vector store')

    return llm, loaded_faiss_vs

def invoke_response_detailed(llm, persona, task, conditions, output_style, vectorstore, query, chat_service):

    # construct initial system message
    sysmsg = f"{persona} {task} {conditions} {output_style}"
    conversation = [SystemMessage(content=sysmsg)]

    # retrieve context from vectorstore
    raw_contexts = chat_service.query_vectorstore(vectorstore, query, k=5)
    if not raw_contexts:
        return "No relevant context found.", 0, None

    formatted_contexts = chat_service.format_contexts(raw_contexts)
  

    maintopic = raw_contexts[0].get("title", None) if raw_contexts else None

    # Build the query with the trimmed context
    context_query = f"""
        Answer query based on context provided.\n
        Context: {formatted_contexts}
        Query: {query}  
        At the end of your answer, add the slide title and page that you used. (only if query is within course scope.)
        Answer concisely and do not use more than 10 sentences.
    """
   
    conversation.append(HumanMessage(content=context_query))

    response, tokens_used = chat_service.get_tokens_used(conversation, llm)

    clean_response = (
        response.replace("System:", "")
        .replace("Human:", "")
        .replace("Answer:", "")
        .strip()
    )
    return clean_response, tokens_used, maintopic, formatted_contexts

def vta_response_generation(llm, filename, vectorstore, chat_service):
    
    qna_storage = []

    data = pd.read_excel(filename)

    for index,row in data.iterrows(): 
        question = row['Question']
        correct_answer = row['Answer']

        # generate response
        response, tokens_used, maintopic, trimmed_contexts = invoke_response_detailed(
            llm,
            persona="You are a teaching assistant at NTU.",
            task="Answer queries on Microprocessor System Design and Development.",
            conditions="If user asks any query beyond Microprocessor System Design and Development,tell the user you are not an expert on the topic.",
            output_style="Keep answers concise, use 10 or less sentences for your response. Add extra information if it helps to clarify your answer",
            vectorstore=vectorstore,
            query=question, chat_service = chat_service
        ) 
        item = {'question': question, 'response': response, 'contexts': trimmed_contexts, 'correct_answer': correct_answer}
        qna_storage.append(item)
    return qna_storage

def generic_llm_judge(llm,query, response, contexts, correct_answer, persona, task, conditions, output_style,evaluation_criteria , chat_service): 
    sysmsg = f"{persona} {task} {conditions} {output_style}"
    conversation = [SystemMessage(content=sysmsg)]

    evaluation_prompt = f"""
    You are a judge evaluating chatbot responses. Your task is to score the response based on the following metric:

    {evaluation_criteria}

    Respond in the following format: 
    Score :intended score 
    Justification: reason for the score given

    Evaluation Details:
    Query: {query}
    Generated Response: {response}
    Context: {contexts}
    Ground truth Answer: {correct_answer}
    """
    print('---evaluation prompt')
    print(evaluation_prompt)

    conversation.append(HumanMessage(content=evaluation_prompt))
    evaluation_response, tokens_used = chat_service.get_tokens_used(conversation, llm)
    clean_evaluation_response = evaluation_response.replace("System:", "").replace("Human:", "").strip()
    
    return clean_evaluation_response, tokens_used

def response_handler(evaluation): 
    print('------')
    print(evaluation)
    score =""
    justification =""
    capture_justification = False

    for line in evaluation.splitlines():
            if "Score:" in line:
                score = line.split("Score:")[-1].strip()
            elif "Justification:" in line:
                justification = line.split("Justification:")[-1].strip()
                capture_justification = True
            elif capture_justification:
                justification += "\n" + line.strip()
            
    return score, justification


def perform_evaluation(llm, qna_storage, metric_name, evaluation_criteria, required_fields,chat_service,):
    """
    Performs evaluations for a specific metric (e.g., relevance, groundedness, correctness).
    """
    results = []
    for item in qna_storage:
        
        inputs = {key: item.get(key, "") for key in required_fields}

        evaluation, tokens_used = generic_llm_judge(
            llm=llm,
            query=inputs.get("question"),
            response=inputs.get("response"),
            contexts=inputs.get("contexts", ""),  
            correct_answer = inputs.get("correct_answer", ""),

            persona="You are a neutral and fair evaluator of chatbot responses.",
            task=f"Evaluate chatbot responses based on {metric_name}.",
            conditions="Focus on the specific evaluation criteria provided.",
            output_style="Provide concise and short justification of less than 5 sentences for scores. Be strict",
            evaluation_criteria=evaluation_criteria,
            chat_service = chat_service
        )

        score, justification = response_handler(evaluation)

        results.append({
            "metric": metric_name,
            "query": inputs.get("question"),
            "response": inputs.get("response"),
            "score": score,
            "justification": justification,
        })
    return results


def save_to_csv(data, filename, fieldnames):
    """
    Saves evaluation results to a CSV file.
    """
    
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def main(): 
    chat_service = ChatService()
    llm = init_judge(chat_service)
    chatllm, vectorstore =  init_vta(chat_service)

    filename = os.path.join(os.path.dirname(__file__), "tests", "clock.xlsx") # include files that you want to evaluate
    if not os.path.exists(filename):
        raise FileNotFoundError(f"File not found: {filename}")
    
    print('Getting responses from vta')
    qna_storage = vta_response_generation(chatllm, filename,vectorstore,chat_service)

    evaluations = [
        {
            "metric_name": "Retrieval Quality",
            "evaluation_criteria": """
            Retrieval Quality:
            - Definition: Assesses the relevance of the retrieved chunks in addressing the user's query.
            - Uses: query and retrieved chunks to evaluate 
            - Score Calculation: Each retrieved chunk (Chunk 1, Chunk 2, etc.) is individually rated as either relevant (1) or not relevant (0). 
            The final score is calculated by summing up the total scores across the 5 chunks.
            - Justification Format: 
            Chunk 1: 1 as [reason]
            Chunk 2: 0 as [reason]
            ..
            """,
            "required_fields": ["question", "contexts"],
            "filename": "retrieval_evaluations.csv"
        },
        {
            "metric_name": "Relevance to Query",
            "evaluation_criteria": """
            Relevance to Query:
            - Definition: The extent to which the generated response directly addresses the user's request.
            - Uses: query and generated response to evaluate 
            - Score: Rate on a scale of 1–10 with justification. Be strict with your scores.
            """,
            "required_fields": ["question", "response"],
            "filename": "relevance_evaluations.csv"
        },
        {
            "metric_name": "Groundedness",
            "evaluation_criteria": """
            Groundedness:
            - Definition: Determines whether the response is based on the provided context or hallucinated.
            - Uses: contexts and response to evaluate
            - Score: Rate on a scale of 1–10 with justification. Be strict with your scores.
            """,
            "required_fields": ["question", "response", "contexts"],
            "filename": "groundedness_evaluations.csv"
        },
        {
            "metric_name": "Correctness",
            "evaluation_criteria": """
            Correctness:
            - Definition: Determines whether the Generated response is factually accurate and aligns with the ground truth answer.
            - Uses: generated response and ground truth answer to evaluate
            - Score: Rate on a scale of 1–10 how close the generated response is to the ground truth answer with justification. Be strict with your scores.
            """,
            "required_fields": ["question", "response", "correct_answer"],
            "filename": "correctness_evaluations.csv"
        },
    ]
    results_dir = os.path.join(os.path.dirname(__file__), "results")

    print('performing evaluations on responses from vta...')
    # Perform evaluations for each metric
    for config in evaluations:
        metric_name = config["metric_name"]
        print('evaluating ' + metric_name)
        metric_results = perform_evaluation(
            llm, qna_storage, config["metric_name"], config["evaluation_criteria"], config["required_fields"], chat_service=chat_service
        )
        savetofilename = os.path.join(results_dir, config["filename"])

        save_to_csv(metric_results, savetofilename, ["metric", "query", "response", "score", "justification"])

        if metric_name == "Retrieval Quality": 
            retrieval_data = [
                {"query": item["question"], 
                 "contexts": item["contexts"]} 
                for item in qna_storage
            ]
            retrieval_filename = os.path.join(results_dir, "retrieval_queries_contexts.csv")
            save_to_csv(retrieval_data, retrieval_filename, ["query", "contexts"])
        


        print('completed evaluation for ' + metric_name)

    print("Evaluations completed and saved to CSV files.")

    
if __name__ == "__main__":
    main()


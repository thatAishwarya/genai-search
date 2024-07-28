import pytest
import time
import requests
from langchain.evaluation import load_evaluator
from langchain.evaluation import EvaluatorType
from langchain_community.llms import Ollama
from langchain_openai import ChatOpenAI
from app_config import SETTINGS
from logging_config import setup_logging

QUERY_ENDPOINT = "http://127.0.0.1:8000/query"

# Initialize logging
logger = setup_logging()

llm1 = Ollama(base_url=SETTINGS["LLM_BASE_URL"], model=SETTINGS["LLM_MODELS"]["llama3.1"]["model_name"], verbose=True)
llm2 = ChatOpenAI(model=SETTINGS["LLM_MODELS"]["gpt-3.5-turbo"]["model_name"], openai_api_key=SETTINGS["OPENAI_API_KEY"])

def evaluate_string_by_criteria(criteria, prediction, input_string, llm=llm2):
    evaluator = load_evaluator(EvaluatorType.CRITERIA, criteria=criteria, llm=llm)
    eval_result = evaluator.evaluate_strings(
        prediction=prediction,
        input=input_string,
    )
    return eval_result

def test_query_similarity():
    sample_query = "What penalties are imposed on companies for non-compliance under the Taxes Consolidation Act, 1997?"
    standard_answer = """the company shall be liable to a penalty not exceeding £500 or, in the case of fraud, £1,000, and such penalty may, without prejudice to any other method of recovery, be proceeded for and recovered summarily in the like manner as in summary proceedings for the recovery of any fine or penalty under any Act relating to the excise.

    (7) For the purpose of regulations made under section 986, no regard shall be had to the relief unless a claim for it has been duly made and admitted.
                        
    (8) For the purposes of section 1080, income tax charged by an assessment—
                        
    (a) shall be regarded as due and payable notwithstanding that relief from the tax (whether by discharge or repayment) is subsequently given on a claim for the relief, but
                        
    (b) shall, unless paid earlier or due and payable later, be regarded as paid, to the extent that relief from tax is due under this Part, on the date of the making of the claim on which the relief is given,
                        
    and section 1081 shall not apply in consequence of any discharge or repayment for giving effect to the relief."""

    # Call the /query endpoint for model 1
    start_time_model_1 = time.time()
    response_model_1 = requests.post(QUERY_ENDPOINT, json={"query": sample_query, "model": "llama3.1"})
    end_time_model_1 = time.time()
    assert response_model_1.status_code == 200
    model_1_answer = response_model_1.json().get("answer", "No answer found.")
    time_taken_model_1 = end_time_model_1 - start_time_model_1

    # Log the response for debugging
    logger.debug(f"llama3.1 answer: {model_1_answer}")

    # Call the /query endpoint for model 2
    start_time_model_2 = time.time()
    response_model_2 = requests.post(QUERY_ENDPOINT, json={"query": sample_query, "model": "gpt-3.5-turbo"})
    end_time_model_2 = time.time()
    assert response_model_2.status_code == 200
    model_2_answer = response_model_2.json().get("answer", "No answer found.")
    time_taken_model_2 = end_time_model_2 - start_time_model_2

    # Log the response for debugging
    logger.debug(f"gpt-3.5-turbo answer: {model_2_answer}")

    # Define criteria for evaluation
    criteria = {
        "relevance": "Is the submission referring to a real quote from the text?",
        "correctness": "Is the submission correct, accurate, and factual?",
        "coherence": "Is the submission coherent, well-structured, and organized?",
        "conciseness": "Is the submission concise and to the point?"
    }

    # Evaluate responses using LangChain criteria evaluators
    eval_result_model_1 = evaluate_string_by_criteria(criteria, model_1_answer, sample_query)
    eval_result_model_2 = evaluate_string_by_criteria(criteria, model_2_answer, sample_query)

    logger.debug(f"Evaluation result for llama3.1: {eval_result_model_1}")
    logger.debug(f"Evaluation result for gpt-3.5-turbo: {eval_result_model_2}")

    # Extract individual criteria results
    # model_1_fulfilled_criteria = {criterion: result for criterion, result in eval_result_model_1.items() if result["value"] == 'Y'}
    # model_2_fulfilled_criteria = {criterion: result for criterion, result in eval_result_model_2.items() if result["value"] == 'Y'}

    # logger.debug(f"Model 1 fulfilled criteria: {model_1_fulfilled_criteria}")
    # logger.debug(f"Model 2 fulfilled criteria: {model_2_fulfilled_criteria}")

    # Check similarity of each model's answer with the standard answer
    similarity_model_1_to_standard = evaluate_string_by_criteria(criteria, model_1_answer, standard_answer)["score"]
    similarity_model_2_to_standard = evaluate_string_by_criteria(criteria, model_2_answer, standard_answer)["score"]

    logger.debug(f"Similarity llama3.1 to Standard: {similarity_model_1_to_standard}")
    logger.debug(f"Similarity gpt-3.5-turbo to Standard: {similarity_model_2_to_standard}")

    # Check similarity of both model answers with each other
    similarity_model_1_to_model_2 = evaluate_string_by_criteria(criteria, model_1_answer, model_2_answer)["score"]

    logger.debug(f"Similarity llama3.1 to gpt-3.5-turbo: {similarity_model_1_to_model_2}")

    logger.debug(f"Time taken by llama3.1: {time_taken_model_1} seconds")
    logger.debug(f"Time taken by gpt-3.5-turbo: {time_taken_model_2} seconds")

    assert similarity_model_1_to_standard >= 0.9  # Replace with desired threshold
    assert similarity_model_2_to_standard >= 0.9  # Replace with desired threshold
    assert similarity_model_1_to_model_2 >= 0.9  # Replace with desired threshold

    # Optionally assert time taken if needed
    # assert time_taken_model_1 <= 15
    # assert time_taken_model_2 <= 15

if __name__ == "__main__":
    pytest.main()

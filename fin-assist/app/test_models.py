import pytest
import time
import requests
from langchain.evaluation import load_evaluator, EvaluatorType
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from app_config import SETTINGS
from logging_config import setup_logging

QUERY_ENDPOINT = "http://127.0.0.1:8000/query"

# Initialize logging
logger = setup_logging()

# Initialize models
llm1 = ChatGroq(model=SETTINGS["LLM_MODELS"]["llama3.1"]["model_name"], api_key=SETTINGS["GROQ_API_KEY"])
llm2 = ChatOpenAI(model=SETTINGS["LLM_MODELS"]["gpt-3.5-turbo"]["model_name"], openai_api_key=SETTINGS["OPENAI_API_KEY"])

# Initialize evaluators
criteria = {
    "relevance": "Is the submission referring to a real quote from the text?",
    "correctness": "Is the submission correct, accurate, and factual?",
    "coherence": "Is the submission coherent, well-structured, and organized?",
    "conciseness": "Is the submission concise and to the point?"
}

evaluator_criteria_llama = load_evaluator(EvaluatorType.CRITERIA, criteria=criteria, llm=llm1)
evaluator_criteria_gpt = load_evaluator(EvaluatorType.CRITERIA, criteria=criteria, llm=llm2)

def evaluate_string_by_criteria(criteria, prediction, input_string, evaluator):
    eval_result = evaluator.evaluate_strings(
        prediction=prediction,
        input=input_string,
    )
    return eval_result

def measure_time(func, *args, **kwargs):
    start_time = time.time()
    result = func(*args, **kwargs)
    elapsed_time = time.time() - start_time
    return result, elapsed_time

def test_query_similarity():
    sample_query = "What penalties are imposed on companies for non-compliance under the Taxes Consolidation Act, 1997?"
    standard_answer = """the company shall be liable to a penalty not exceeding £500 or, in the case of fraud, £1,000, and such penalty may, without prejudice to any other method of recovery, be proceeded for and recovered summarily in the like manner as in summary proceedings for the recovery of any fine or penalty under any Act relating to the excise.

    (7) For the purpose of regulations made under section 986, no regard shall be had to the relief unless a claim for it has been duly made and admitted.
                        
    (8) For the purposes of section 1080, income tax charged by an assessment—
                        
    (a) shall be regarded as due and payable notwithstanding that relief from the tax (whether by discharge or repayment) is subsequently given on a claim for the relief, but
                        
    (b) shall, unless paid earlier or due and payable later, be regarded as paid, to the extent that relief from tax is due under this Part, on the date of the making of the claim on which the relief is given,
                        
    and section 1081 shall not apply in consequence of any discharge or repayment for giving effect to the relief."""

    try:
        # Call the /query endpoint for model 1
        model_1_response, time_taken_model_1 = measure_time(requests.post, QUERY_ENDPOINT, json={"query": sample_query, "model": "llama3.1"})
        assert model_1_response.status_code == 200
        model_1_answer = model_1_response.json().get("answer", "No answer found.")
    except requests.RequestException as e:
        logger.error(f"Request failed for llama3.1: {e}")
        pytest.fail(f"Request failed for llama3.1: {e}")

    logger.debug(f"llama3.1 answer: {model_1_answer}")

    try:
        # Call the /query endpoint for model 2
        model_2_response, time_taken_model_2 = measure_time(requests.post, QUERY_ENDPOINT, json={"query": sample_query, "model": "gpt-3.5-turbo"})
        assert model_2_response.status_code == 200
        model_2_answer = model_2_response.json().get("answer", "No answer found.")
    except requests.RequestException as e:
        logger.error(f"Request failed for gpt-3.5-turbo: {e}")
        pytest.fail(f"Request failed for gpt-3.5-turbo: {e}")

    logger.debug(f"gpt-3.5-turbo answer: {model_2_answer}")

    # Evaluate responses using both evaluators
    results_model_1_llama_criteria, time_taken_model_1_llama = measure_time(
        evaluate_string_by_criteria, criteria, model_1_answer, sample_query, evaluator_criteria_llama
    )
    results_model_2_gpt_criteria, time_taken_model_2_gpt = measure_time(
        evaluate_string_by_criteria, criteria, model_2_answer, sample_query, evaluator_criteria_gpt
    )

    logger.debug(f"Evaluation result for llama3.1 using llama evaluator: {results_model_1_llama_criteria}")
    logger.debug(f"Evaluation result for gpt-3.5-turbo using gpt evaluator: {results_model_2_gpt_criteria}")

    # Check similarity of each model's answer with the standard answer
    similarity_model_1_to_standard_llama, _ = measure_time(
        evaluate_string_by_criteria, criteria, model_1_answer, standard_answer, evaluator_criteria_llama
    )
    similarity_model_2_to_standard_gpt, _ = measure_time(
        evaluate_string_by_criteria, criteria, model_2_answer, standard_answer, evaluator_criteria_gpt
    )

    logger.debug(f"Similarity llama3.1 to Standard using llama evaluator: {similarity_model_1_to_standard_llama['score']}")
    logger.debug(f"Similarity gpt-3.5-turbo to Standard using gpt evaluator: {similarity_model_2_to_standard_gpt['score']}")

    # Check similarity of both model answers with each other
    similarity_model_1_to_model_2_llama, _ = measure_time(
        evaluate_string_by_criteria, criteria, model_1_answer, model_2_answer, evaluator_criteria_llama
    )
    similarity_model_1_to_model_2_gpt, _ = measure_time(
        evaluate_string_by_criteria, criteria, model_1_answer, model_2_answer, evaluator_criteria_gpt
    )

    logger.debug(f"Similarity llama3.1 to gpt-3.5-turbo using llama evaluator: {similarity_model_1_to_model_2_llama['score']}")
    logger.debug(f"Similarity llama3.1 to gpt-3.5-turbo using gpt evaluator: {similarity_model_1_to_model_2_gpt['score']}")

    logger.debug(f"Time taken by llama3.1: {time_taken_model_1} seconds")
    logger.debug(f"Time taken by gpt-3.5-turbo: {time_taken_model_2} seconds")

    # Assertions
    assert similarity_model_1_to_standard_llama['score'] >= 0.9, "llama3.1 to Standard (llama evaluator) below threshold"
    assert similarity_model_2_to_standard_gpt['score'] >= 0.9, "gpt-3.5-turbo to Standard (gpt evaluator) below threshold"
    assert similarity_model_1_to_model_2_llama['score'] >= 0.9, "llama3.1 to gpt-3.5-turbo (llama evaluator) below threshold"
    assert similarity_model_1_to_model_2_gpt['score'] >= 0.9, "llama3.1 to gpt-3.5-turbo (gpt evaluator) below threshold"

    # Optionally assert time taken if needed
    assert time_taken_model_1 <= 15, "Time taken by llama3.1 exceeds threshold"
    assert time_taken_model_2 <= 15, "Time taken by gpt-3.5-turbo exceeds threshold"

if __name__ == "__main__":
    pytest.main()

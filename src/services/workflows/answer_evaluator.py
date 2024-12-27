# """
# This module implements the functionality for evaluating answers based on predefined criteria, 
# including calculating scores using weighted averages, and storing results in a database.
# """

# import json
# import threading
# import logging
# from collections import defaultdict
# from app.llm import llm
# from app.prompts import answer_evaluator_prompt
# from app.DAO.Interview_Question_Evaluation import add_question_evaluation
# from app.DAO.Chat_History import get_chat_history, add_candidate_answer
# from app.DAO.Subcriteria import fetch_subcriteria


# # Set up logging for tracking application behavior
# logger = logging.getLogger(__name__) # Get logger instance for the current module
# logger.setLevel(logging.INFO) # Set logging level to INFO
# formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s:%(funcName)s') # Log format
# file_handler = logging.FileHandler('noha_ai_prototype.log') # Log events to a file
# file_handler.setFormatter(formatter) # Attach formatter to handler
# logger.addHandler(file_handler) # Add handler to logger


# # async def evaluate_ans_with_eval_subcriteria(sub_criteria, question, answer, interview_id, question_id):
# #     """
# #     Evaluates the answer against sub_criteria and calculates a final score.

# #     Args:
# #         sub_criteria (list): List of subcriterion to evaluate.
# #         question (str): The interview question.
# #         answer (str): The provided answer.
# #         interview_id (int): Unique ID of the interview.
# #         question_id (int): Unique ID of the question.

# #     Returns:
# #         dict: Evaluation results, accumulated results, and final score.
# #     """

# #     try:
# #         # Group sub_criteria by criteria_id
# #         try:
# #             grouped_subcriteria = defaultdict(list)
# #             for sub_criterion in sub_criteria:
# #                 if sub_criterion["question_id"] == question_id:
# #                     grouped_subcriteria[sub_criterion["criteria_id"]].append(sub_criterion)
# #         except KeyError as key_err:
# #             logger.critical(f"Missing required key in sub_criteria: {key_err}")
# #             raise KeyError(f"Missing required key in sub_criteria: {key_err}") from key_err
# #         except TypeError as type_err:
# #             logger.critical(f"sub_criteria must be a list of dictionaries: {type_err}")
# #             raise TypeError(f"sub_criteria must be a list of dictionaries: {type_err}") from type_err

# #         # Retrieve chat history from db
# #         try:
# #             retrieved_chat_history = await get_chat_history(interview_id)
# #             logger.info("Succesfully retrieved chat history from db")
# #         except Exception as db_err:
# #             logger.critical(f"Failed to retrieve chat history from db: {db_err}")
# #             raise Exception(f"Database error while retrieving chat history: {db_err}") from db_err
        
# #         try:
# #             retrieved_chat_history.append({"question": question, "answer": answer})
# #         except AttributeError as attr_err:
# #             logger.critical(f"Failed to append to retrieved chat history: {attr_err}")
# #             raise AttributeError(f"Failed to append to retrieved chat history: {attr_err}") from attr_err

# #         # Final results storage
# #         evaluation_results = {}
# #         total_criteria_count = [0]
# #         accumulated_results_all_criteria = {}

# #         # Create and start threads
# #         try:
# #             logger.info("Threading of evaluating answer according to sub_criteria started")
# #             total_criteria_lock = threading.Lock()
# #             threads = []

# #             for criteria_id, sub_criteria in grouped_subcriteria.items():
# #                 thread = threading.Thread(
# #                     target=evaluate_answer_with_criteria,
# #                     args=(criteria_id, sub_criteria, retrieved_chat_history, evaluation_results, accumulated_results_all_criteria, total_criteria_count, total_criteria_lock)
# #                 )
# #                 threads.append(thread)
# #                 thread.start()

# #             # Wait for all threads to complete
# #             for thread in threads:
# #                 thread.join()
# #         except Exception as thread_err:
# #             logger.critical(f"Threading operation failed: {thread_err}")
# #             raise Exception(f"Threading operation failed: {thread_err}") from thread_err

# #         logger.info("Threading of evaluating answer according to sub_criteria completed")

# #         # Calculate final score
# #         try:
# #             logger.info("Calculating final_score")
# #             total_score_count = sum(accumulated_results_all_criteria.values())
# #             final_score = round(total_score_count / total_criteria_count[0], 2)
# #         except ZeroDivisionError as zero_div_err:
# #             logger.critical(f"No criteria found for scoring: {zero_div_err}")
# #             raise ZeroDivisionError("No criteria found for scoring.") from zero_div_err

# #         # Save results to the database (including the full accumulated results and sub_criteria)
# #         try:
# #             await add_question_evaluation(interview_id, question_id, final_score, evaluation_results, accumulated_results_all_criteria)
# #             logger.info("Successfully inserted question evaluation results in db")
# #         except Exception as db_insert_err:
# #             logger.critical(f"Failed to insert question evaluation results in db: {db_insert_err}")
# #             raise Exception(f"Database error while inserting question evaluation: {db_insert_err}") from db_insert_err
        
# #         # Save candidate answer to the database to maintain chat_history
# #         try:
# #             await add_candidate_answer(interview_id, question_id, answer)
# #             logger.info("Successfully inserted current chat in db")
# #         except Exception as db_chat_err:
# #             logger.critical(f"Failed to insert current chat in db: {db_chat_err}")
# #             raise Exception(f"Database error while inserting current chat: {db_chat_err}") from db_chat_err

# #         # Return the final evaluation results along with accumulated data for all criteria
# #         logger.info("Successfully generated evaluation of the provided answer")
# #         return {
# #             "evaluation_results": evaluation_results,
# #             "accumulated_results_all_criteria": accumulated_results_all_criteria,
# #             "final_score": final_score
# #         }
    
# #     except (KeyError, TypeError, AttributeError, ZeroDivisionError) as specific_err:
# #         logger.critical(f"Specific error in evaluate_ans_with_eval_subcriteria: {specific_err}")
# #         raise specific_err
# #     except Exception as ex:
# #         logger.critical(f"Unexpected error in evaluate_ans_with_eval_subcriteria: {ex}")
# #         raise Exception(f"Unexpected error in evaluate_ans_with_eval_subcriteria: {ex}")

# # def evaluate_answer_with_criteria(criteria_id, sub_criteria, chat_history, evaluation_results, accumulated_results_all_criteria, total_criteria_count, total_criteria_lock):
    
# #     """
# #     Processes and evaluates a specific criteria of sub_criteria.

# #     Args:
# #         criteria_id (int): ID of the criteria being processed.
# #         sub_criteria (list): List of sub_criterion for the criteria.
# #         chat_history (list): List containing the chat history for the evaluation.
# #         evaluation_results (dict): Storage for evaluation results.
# #         accumulated_results_all_criteria (dict): Storage for accumulated results.
# #         total_criteria_count (list): Shared counter for total criteria evaluated.
# #         total_criteria_lock (threading.Lock): Lock for updating shared counter.
# #     """
    
# #     try:
# #         print(f"Evaluating Criteria ID: {criteria_id}")

# #         # Extract criteria and weights
# #         try:
# #             refactored_sub_criteria = {str(idx + 1): sub_criterion["sub_criteria"] for idx, sub_criterion in enumerate(sub_criteria)}
# #             sub_criteria_weights = [sub_criterion["weight"] for sub_criterion in sub_criteria]
# #         except KeyError as key_err:
# #             logger.critical(f"Missing required key in sub_criteria: {key_err}")
# #             raise KeyError(f"Missing required key in sub_criteria: {key_err}") from key_err
# #         except TypeError as type_err:
# #             logger.critical(f"sub_criteria must be a list of dictionaries: {type_err}")
# #             raise TypeError(f"sub_criteria must be a list of dictionaries: {type_err}") from type_err

# #         # Ensure weights are numeric
# #         if not all(isinstance(weight, (int, float)) for weight in sub_criteria_weights):
# #             logger.critical(f"Invalid weights in sub_criteria_weights: {sub_criteria_weights}")
# #             raise ValueError(f"Invalid weights in sub_criteria_weights: {sub_criteria_weights}")

# #         evaluation_criteria_results = {}

# #         # Generate evaluation chain response
# #         try:
# #             llm_evaluation_response = generate_evaluation_llm_response(refactored_sub_criteria, chat_history)
# #             evaluation_criteria_results = llm_evaluation_response
# #             logger.info(f"Successfully completed evaluation of answer w.r.t. sub_criteria of criteria: {criteria_id}")
# #         except Exception as e:
# #             print(f"Error evaluating sub_criteria for criteria {criteria_id}: {e}")
# #             logger.critical(f"Error evaluating sub_criteria for criteria {criteria_id}: {e}")
# #             raise Exception(f"Error evaluating sub_criteria for criteria {criteria_id}: {e}")

# #         print(f"Accumulating Criteria ID: {criteria_id}")

# #         # Accumulate scores for the criteria
# #         try:
# #             score_accumulator_response = generate_score_accumulator_llm_response(sub_criteria_weights, evaluation_criteria_results)
# #             logger.info(f"Successfully completed accumulation of sub_criteria results of criteria: {criteria_id}")
# #         except Exception as ex:
# #             print(f"Error in accumulation for criteria {criteria_id}: {ex}")
# #             logger.critical(f"Error in accumulation for criteria {criteria_id}: {ex}")
# #             raise Exception(f"Error in accumulation for criteria {criteria_id}: {ex}")

# #         # Store results for the criteria
# #         evaluation_results[criteria_id] = {
# #             "criteria": refactored_sub_criteria,
# #             "responses": evaluation_criteria_results,
# #             "accumulated_result": score_accumulator_response  # Include the accumulated result
# #         }

# #         # Add the accumulated result for this criteria to the global accumulated results
# #         accumulated_results_all_criteria[criteria_id] = score_accumulator_response

# #         # Update total criteria count
# #         with total_criteria_lock:
# #             total_criteria_count[0] += 1

# #         logger.info(f"Successfully completed evaluation of criteriq: {criteria_id}")
# #         return None
    
# #     except KeyError as key_err:
# #         logger.critical(f"KeyError in evaluate_answer_with_criteria for criteria {criteria_id}: {key_err}")
# #         raise key_err
# #     except TypeError as type_err:
# #         logger.critical(f"TypeError in evaluate_answer_with_criteria for criteria {criteria_id}: {type_err}")
# #         raise type_err
# #     except ValueError as val_err:
# #         logger.critical(f"ValueError in evaluate_answer_with_criteria for criteria {criteria_id}: {val_err}")
# #         raise val_err
# #     except Exception as ex:
# #         logger.critical(f"Unexpected error in evaluate_answer_with_criteria for criteria {criteria_id}: {ex}")
# #         raise Exception(f"Unexpected error in evaluate_answer_with_criteria for criteria {criteria_id}: {ex}")


# async def evaluate_answer(input_request):
#     """
#     Orchestrates the evaluation process for a given query.
    
#     Args:
#         input (GenerateEvaluation): The request body containing the evaluation details.
#             - question_id (int): The unique identifier of the question to be evaluated.
#             - question (str): The text of the question.
#             - interview_id (int): The unique identifier of the interview session.
#             - answer (str): The candidate's answer to be evaluated.
    
#     Returns:
#         dict: A response containing the evaluation results.
#     """

#     try:
#         try:
#             question_id = input_request.question_id
#             question = input_request.question
#             interview_id = input_request.interview_id
#             candidate_answer = input_request.answer
#         except AttributeError as attr_err:
#             logger.critical(f"Input object missing required attributes: {attr_err}")
#             raise AttributeError(f"Input object missing required attributes: {attr_err}") from attr_err

#         subcriteria = await fetch_subcriteria(question_id)
#         chat_history = await get_chat_history(interview_id)
#         chat_history.append({"question": question, "answer": candidate_answer})
#         llm_evaluation_response = generate_evaluation_llm_response(question, candidate_answer, subcriteria,  chat_history)
#         score_accumulator_response = generate_score_accumulator_llm_response(sub_criteria_weights, evaluation_criteria_results)
#         logger.info("Calculating final_score")
#         total_score_count = sum(accumulated_results_all_criteria.values())
#         final_score = round(total_score_count / total_criteria_count[0], 2)
#         logger.info("Successfully retrieved sub metrics from db")

        # try:
        #     await add_question_evaluation(interview_id, question_id, final_score, evaluation_results, accumulated_results_all_criteria)
        #     logger.info("Successfully inserted question evaluation results in db")
        # except Exception as db_insert_err:
        #     logger.critical(f"Failed to insert question evaluation results in db: {db_insert_err}")
        #     raise Exception(f"Database error while inserting question evaluation: {db_insert_err}") from db_insert_err
        # try:
        #     await add_candidate_answer(interview_id, question_id, answer)
        #     logger.info("Successfully inserted current chat in db")
        # except Exception as db_chat_err:
        #     logger.critical(f"Failed to insert current chat in db: {db_chat_err}")
        #     raise Exception(f"Database error while inserting current chat: {db_chat_err}") from db_chat_err







# #         try:
# #             evaluation_results = await evaluate_ans_with_eval_subcriteria(subcriteria, question, candidate_answer, interview_id, question_id)
# #             logger.info("evaluate_ans_with_eval_subcriteria call successful")
# #         except Exception as ex:
# #             logger.critical(f"evaluate_ans_with_eval_subcriteria call failed: {ex}")
# #             raise Exception(f"evaluate_ans_with_eval_subcriteria call failed: {ex}")
        
# #         return evaluation_results
    
#     except AttributeError as specific_err:
#         logger.critical(f"Specific error in evaluation process: {specific_err}")
#         raise specific_err
#     except Exception as ex:
#         logger.critical(f"Unexpected error in evaluation process: {ex}")
#         raise Exception(f"Unexpected error in evaluation process: {ex}")




# # def generate_score_accumulator_llm_response(sub_criteria_weights, evaluation_criteria_results):

# #     """
# #     Aggregates evaluation scores for multiple sub_criterion and calculates an overall score.

# #     Args:
# #         sub_criteria_weights (list): Weights associated with each sub_criterion.
# #         evaluation_criteria_results (dict): Evaluation results for each sub_criterion.

# #     Returns:
# #         float: The accumulated score.
# #     """

# #     try:
# #         # Validate input types
# #         if not isinstance(sub_criteria_weights, list):
# #             logger.critical(f"sub_criteria_weights should be a list but got {type(sub_criteria_weights)}")
# #             raise TypeError("sub_criteria_weights must be a list of numeric values.")
# #         if not isinstance(evaluation_criteria_results, dict):
# #             logger.critical(f"evaluation_criteria_results should be a dictionary but got {type(evaluation_criteria_results)}")
# #             raise TypeError("evaluation_criteria_results must be a dictionary with sub_criteria scores.")

# #         # Convert and validate scores in evaluation_criteria_results
# #         try:
# #             sub_criteria_evaluated_scores = [
# #                 int(score) for score in evaluation_criteria_results.values()
# #             ]
# #         except ValueError as value_err:
# #             logger.critical(f"Invalid score value in evaluation_criteria_results: {value_err}")
# #             raise ValueError(f"Invalid score value in evaluation_criteria_results: {value_err}") from value_err
# #         except TypeError as type_err:
# #             logger.critical(f"Error converting scores in evaluation_criteria_results: {type_err}")
# #             raise TypeError(f"Non-numeric value found in evaluation_criteria_results: {type_err}") from type_err

# #         # Ensure weights and scores have the same length
# #         if len(sub_criteria_weights) != len(sub_criteria_evaluated_scores):
# #             logger.critical(
# #                 f"Mismatch between weights ({len(sub_criteria_weights)}) and scores ({len(sub_criteria_evaluated_scores)})."
# #             )
# #             raise ValueError(
# #                 f"Mismatch between the number of weights and scores: {len(sub_criteria_weights)} vs {len(sub_criteria_evaluated_scores)}"
# #             )

# #         # Calculate the accumulated score
# #         try:
# #             accumulated_score = calculate_score(sub_criteria_weights, sub_criteria_evaluated_scores)
# #         except Exception as calc_err:
# #             logger.critical(f"Error in calculating accumulated score: {calc_err}")
# #             raise Exception(f"Error in calculating accumulated score: {calc_err}") from calc_err

# #         return accumulated_score
    
# #     except Exception as ex:
# #         logger.critical(f"Error in creating accumulator response: {ex}")
# #         raise Exception(f"Error in creating accumulator response: {ex}")
    
# # def calculate_score(weights, scores):
# #     """
# #     Calculates the weighted average score for a set of sub_criterion.

# #     Args:
# #         weights (list): A list of weights for each sub_criterion.
# #         scores (list): A list of scores for each sub_criterion.

# #     Returns:
# #         float: The weighted average score, rounded to two decimal places.
# #     """
# #     try:
# #         # Validate input types
# #         if not isinstance(weights, list) or not isinstance(scores, list):
# #             logger.critical(f"weights and scores must be lists. Got {type(weights)} and {type(scores)}.")
# #             raise TypeError("Both weights and scores must be lists.")

# #         # Validate that all elements in weights and scores are numeric
# #         if not all(isinstance(w, (int, float)) for w in weights):
# #             logger.critical(f"weights contains non-numeric values: {weights}")
# #             raise TypeError("All elements in weights must be numeric.")
# #         if not all(isinstance(s, (int, float)) for s in scores):
# #             logger.critical(f"scores contains non-numeric values: {scores}")
# #             raise TypeError("All elements in scores must be numeric.")

# #         # Validate that weights and scores have the same length
# #         if len(weights) != len(scores):
# #             logger.critical(f"Mismatch between weights ({len(weights)}) and scores ({len(scores)}).")
# #             raise ValueError("The length of weights and scores must be the same.")

# #         # Calculate total weight and weighted score
# #         try:
# #             total_weight = sum(weights)
# #             weighted_score = sum(w * s for w, s in zip(weights, scores))

# #             # Handle division by zero gracefully
# #             accumulated_score = round((weighted_score / total_weight), 2) if total_weight != 0 else 0
# #         except ZeroDivisionError as zero_div_err:
# #             logger.critical(f"Total weight is zero, cannot calculate weighted score: {zero_div_err}")
# #             raise ZeroDivisionError("Total weight cannot be zero.") from zero_div_err

# #         return accumulated_score

# #     except (TypeError, ValueError, ZeroDivisionError) as specific_err:
# #         logger.critical(f"Specific error in calculating score: {specific_err}")
# #         raise specific_err
# #     except Exception as ex:
# #         logger.critical(f"Unexpected error in calculating score: {ex}")
# #         raise Exception(f"Unexpected error in calculating score: {ex}")

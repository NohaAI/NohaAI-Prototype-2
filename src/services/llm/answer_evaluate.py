
# from app.prompts import answer_evaluator_prompt


# def generate_evaluation_llm_response(criteria, chat_history):

#     """
#     Handles the evaluation of the provided answer based on the given criteria using a large language model.

#     Args:
#         criteria (dict): The criteria for assessing the answer.
#         chat_history (list): The chat history containing the conversation context.

#     Returns:
#         dict: The response from the evaluation chain.
#     """

#     try:
#         try:
#             evaluation_prompt = answer_evaluator_prompt.AnswerEval.get()
#         except AttributeError as attr_err:
#             logger.critical(f"Error accessing evaluation prompt: {attr_err}")
#             raise AttributeError(f"Error accessing evaluation prompt: {attr_err}") from attr_err

#         # Retrieve the language model
#         try:
#             evaluation_llm = llm.LLM.get_openai_model()
#             # eval_llm = llm.LLM.get_mistral_model()
#         except AttributeError as attr_err:
#             logger.critical(f"Error accessing LLM model: {attr_err}")
#             raise AttributeError(f"Error accessing LLM model: {attr_err}") from attr_err

#         # Combine the evaluation prompt and the language model into a chain
#         try:
#             evaluation_chain = evaluation_prompt | evaluation_llm
#         except Exception as chain_err:
#             logger.critical(f"Error creating evaluation chain: {chain_err}")
#             raise Exception(f"Error creating evaluation chain: {chain_err}") from chain_err

#         # Invoke the evaluation chain
#         try:
#             llm_response = evaluation_chain.invoke({'chat_history': chat_history, 'eval_param': criteria})
#         except TypeError as type_err:
#             logger.critical(f"Error invoking evaluation chain with provided parameters: {type_err}")
#             raise TypeError(f"Error invoking evaluation chain: {type_err}") from type_err
#         except Exception as invoke_err:
#             logger.critical(f"Error during chain invocation: {invoke_err}")
#             raise Exception(f"Error during chain invocation: {invoke_err}") from invoke_err
        
#         try:
#             evaluation_response = json.loads(llm_response.content)
#         except ValueError as value_err:
#             logger.critical(f"Error parsing JSON response from evaluation chain: {value_err}")
#             raise ValueError(f"Invalid JSON response: {value_err}") from value_err
#         except AttributeError as attr_err:
#             logger.critical(f"Error accessing content of evaluation response: {attr_err}")
#             raise AttributeError(f"Error accessing evaluation response content: {attr_err}") from attr_err

#         logger.info("Successfully created evaluator chain response")
#         return evaluation_response
    
#     except (AttributeError, TypeError, ValueError) as specific_err:
#         logger.critical(f"Specific error in generating evaluator chain response: {specific_err}")
#         raise specific_err
#     except Exception as ex:
#         logger.critical(f"Unexpected error in creating evaluator chain response: {ex}")
#         raise Exception(f"Unexpected error in creating evaluator chain response: {ex}")
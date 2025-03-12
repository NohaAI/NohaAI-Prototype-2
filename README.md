# NohaAI-Prototype-2

## Updates
[@07Mar25 - @09Mar25]
- change the old greeting to an officially chosen greeting message (FIXED)
- create a structure for configuration; conf/ with three configuration files (FIXED)
    - collect all constants suitably into the configuration files
    - refactored and added about 20 default constants in configuration
- correct the wrong function name "intialize()" in app.py (FIXED)
- handle the question COMPLEXITY logic
    - initialize the COMPLEXITY TO THE DEFAULT value in initialize() function itself
- initialize the following in initialize/
    - session_state
    - chat_history
    - assessment
- refactored exchange of parameters between client and server
    - candidate_dialogue packed in session_state
- complete redesigning and refactoring of databases
    - refactor src/dao/chat_history.py to DAO python class
    - decouple FastAPI functionality to src/api/chat_history.py
    - model the chat_history record and definition in src/dao/chat_history_data/chat_history_record.py
    - update and alter the chat_history table properties fi. turn_input -> bot_dialogue etc.
- complete redesigning and refactoring of QuestionEvaluation table
    - rename the table to assessment
    - refactor the src/schemas/QuestionEvaluationRequest and QuestionEvaluationResponse
    - refactor src/dao/assessment.py to DAO python class
    - decouple the FastAPI functionality to src/api/chat/asssessment.py
    - model the assessment record and definition in src/dao/assessment_data/assessment_record.py
    - miscellaneous code refactoring owing to improper passing of arguments with inconsistent variable names
- refactored the signatures to and from the call to get_next_response
- client code changed to add candidate_dialogue to chat_history and session_state instead of appending separately in the request to server
- create a helper function to pretty print session_state (SS), chat_history(CH), assessment (AM) structures
-   correct the numerous loggers and unnecessary print statements
- correct the logic for generate_action_overrides
- correct if/else issue and other logic in perform_action
- commented validate_input() for refactoring or deleting later
- fix bugs when accessing new DAO class, correct the AssessmentRecord and the CRUD functions (program now runs across guardrails)
- test and add right logic or counters in process_technical and non_process_technical functions
    - add constants for modeling labels within technical_labels group which are reasonable and must not increment guardrail counts NON_TECHNICAL_UNREASONABLE_LABELS
- changed the field 'score' in the AssessmentRecord object to 'primary_question_score'
-   made similar changes in relevant prompts and the database table assessment and the DAO access functions
- completely refactore answer_classifier as solution_classifier 
    - modeling labels from the two classifier prompts as label_class1 and label_class2
- refactor answer_evaluator to solution_evaluator that does evaluation
- test the ASR output multiple times with en-US and en-IN, both seem equally bad (need to test this thoroughly or fine-tune the webspeech kit (long term))

[27/12/2024]
- Created this version-2 repository "NohaAI-Prototype-2" for complete code review  
### TODO
1. Merge Final_Feedback and Final_Evaluation in DAO (Toyesh)
2. Create a DB_Schema.sql file with 10 create table statements reflecting the current table schema (Toyesh)
3. Create a dump of the current postgresSQL database and add it to test_data.sql. This dump should not contain any create statements (Toyesh)
4. Update the greeter endpoint to call the greeter service(Nabiha)
5. Use the greeter service to call the DAO to interview,users,questions and return the response(Toyesh) 
6. Remove ds_criterion_to_id_map in batch_insert and review design for Criterion table (should be able to retrieve criterion_id)
7. Write test-cases for all APIs
8. Refactor/rename src.services.llm.prompts/subcriteria.py to subcriteria_generator_prompt.py

## Git commit convention followed in these repositories

### Type convention (commit belongs to ...)
```python
feat: addition of some new features
add: changes to add new capability or functions
cut: removing the capability or functions
fix: a bug fix
bump: increasing the versions or dependency versions
build: changes to build system or external dependencies
make: change to the build process, or tooling, or infra
ci: changes to CI configuration files and scripts
doc: changes to the documentation
test: adding missing tests or correcting existing tests
chore: changes for housekeeping (avoiding this will force more meaningful message)
refactor: a code change that neither fixes a bug nor adds a feature
style: changes to the code that do not affect the meaning
optimize/perf: a code change that improves performance
revert: reverting an accidental commit
research: adding code to explore some functionalities
```

### Type convention (branch belongs to ...)
setup_env: making changes that affect the setup environment; fixing stuff with pip requirements, package dependencies and other documentation

### Format convention
* Must not contain a periods(.) at the end
* Must not capitalize the first letter
* Do not use issue identifiers as scopes
* Use imperatives

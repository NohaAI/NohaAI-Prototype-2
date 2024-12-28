# NohaAI-Prototype-2

## Updates
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

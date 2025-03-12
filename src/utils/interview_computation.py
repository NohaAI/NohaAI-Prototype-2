from src.utils import logger

# Initialize logger
logger = logger.get_logger(__name__)

async def compute_turn_score(assessment_payload=None):
    try:
        if not assessment_payload or not isinstance(assessment_payload, dict):
            logger.error("Invalid assessment_payload: Expected a non-empty dictionary.")
            return None

        criteria = assessment_payload.get("criteria")
        if not criteria or not isinstance(criteria, list):
            logger.error("Criterion list is empty or not a list.")
            return None

        ### reinitialize these fields to avoid scores being appended to (n-1)th turn scores
        assessment_payload['subcriteria_scores'] = []
        assessment_payload['criteria_scores'] = []

        # Iterate through criteria list
        for count, criterion in enumerate(criteria):
            logger.info(f"Processing criteria number: {count}")

            subcriteria_weighted_running_total = 0
            subcriteria = criterion.get("subcriteria", [])

            if not isinstance(subcriteria, list):
                logger.error(f"Invalid subcriteria format in criterion {count}. Expected a list.")
                return None

            for subcriterion in subcriteria:
                subcriterion_score = subcriterion.get("score")
                subcriterion_weight = subcriterion.get("weight")

                if subcriterion_score is None or not isinstance(subcriterion_score, (int, float)):
                    logger.error(f"Missing or invalid 'score' in subcriterion: {subcriterion}")
                    return None

                if subcriterion_weight is None or not isinstance(subcriterion_weight, (int, float)):
                    logger.error(f"Missing or invalid 'weight' in subcriterion: {subcriterion}")
                    return None

                subcriterion_weighted_score = round(subcriterion_score * (subcriterion_weight * 0.1),2)
                subcriteria_weighted_running_total += subcriterion_weighted_score

                logger.debug(f"subcriterion_weighted_score: {subcriterion_weighted_score}")
                logger.debug(f"subcriteria_weighted_running_total: {subcriteria_weighted_running_total}")

                if "subcriteria_scores" not in assessment_payload or not isinstance(assessment_payload["subcriteria_scores"], list):
                    logger.error("Invalid or missing 'subcriteria_scores' in assessment_payload.")
                    return None

                assessment_payload["subcriteria_scores"].append(subcriterion_weighted_score)
                logger.debug(f"Added subcriterion_weighted_score: {assessment_payload['subcriteria_scores']}")

            # Validate criterion["calculated_score"]
            if "calculated_score" not in criterion or not isinstance(criterion.get("calculated_score"), (int, float)):
                logger.error(f"Criterion[{count}] score field is missing or invalid.")
                return None

            criterion_score = round((subcriteria_weighted_running_total / len(subcriteria)), 2)
            criterion["calculated_score"] = criterion_score
            logger.info(f"criterion['calculated_score']: {criterion['calculated_score']}")

            # Validate criterion["weight"]
            criterion_weight = criterion.get("weight")
            if criterion_weight is None or not isinstance(criterion_weight, (int, float)):
                logger.error(f"Criterion[{count}] weight field is missing or invalid.")
                return None

            criterion_weighted_score = round((criterion["calculated_score"] * (criterion_weight * 0.1)), 2)
            logger.info(f"criterion_weighted_score: {criterion_weighted_score}")

            if "criteria_scores" not in assessment_payload or not isinstance(assessment_payload["criteria_scores"], list):
                logger.error("Invalid or missing 'criteria_scores' in assessment_payload.")
                return None

            assessment_payload["criteria_scores"].append(criterion_weighted_score)
            logger.debug(f"Added criterion_weighted_score: {assessment_payload['criteria_scores']}")

        if not assessment_payload["criteria_scores"]:
            logger.error("No valid criteria scores found. Final score calculation aborted.")
            return None

        # Compute final score
        criteria_final_score = sum(assessment_payload["criteria_scores"]) / len(assessment_payload["criteria_scores"])

        if "final_score" not in assessment_payload or not isinstance(assessment_payload.get("final_score"), (int, float)):
            logger.error("Invalid or missing 'final_score' in assessment_payload.")
            return None

        assessment_payload["final_score"] = round(criteria_final_score, 2)
        logger.info(f"Final computed scores - criteria_scores: {assessment_payload['criteria_scores']}, final_score: {assessment_payload['final_score']}")

        return assessment_payload

    except Exception as e:
        logger.exception(f"Unexpected error in compute_turn_score: {str(e)}")
        return None


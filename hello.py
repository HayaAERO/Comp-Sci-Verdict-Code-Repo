import pandas as pd
import json
import os

# Helps work with folders
# Instead of writing:
# data/validation/file.csv
#Write:
# os.path.join("data","validation", "file.csv")
from enum import Enum
#Avoid spelling mistakes
# Instead of: "INVALID_VERDICT"
# Write: ValidationFlag.INVALID_VERDICT

# ==============================================================================
# TODOs for Refactoring:
# 1. Refactor magic numbers and strings (e.g., file paths, skill names)
#    into a separate config.py file.
# 2. Refactor validation_flags into an Enum class (see below).
# 3. Refactor column names into top-level variables.
# ==============================================================================
#FIX HERE: All Enum classes placed at top-level so they can be accessed anywhere without NameError
class ValidationFlag(Enum):
    """TODO: Expand this Enum for all validation rules and use instead of strings"""
    # "MIN_SKILLS_COUNT_VIOLATION" is the string value
    MIN_SKILLS_COUNT = "MIN_SKILLS_COUNT_VIOLATION"
    MISSING_ACTIVE_LISTENING = "SEMINAR_MISSING_ACTIVE_LISTENING"
    MISSING_SPEAKING = "SEMINAR_MISSING_SPEAKING"
    INVALID_VERDICT = "INVALID_VERDICT"
    INVALID_CONFIDENCE = "INVALID_CONFIDENCE"
    INVALID_COURSE_CODE = "INVALID_COURSE_CODE"
    MISSING_COURSE_TITLE = "MISSING_COURSE_TITLE"

class Verdict(Enum):
        AUTOMATING = "Automating"
        TRANSFORMING = "Transforming"
        UNTOUCHED = "Untouched"
    
class Confidence(Enum):
        HIGH = "high"
        MEDIUM = "medium"
        LOW = "low"
class ManualAction(Enum):
        UNREVIEWED = "unreviewed"
        ACCEPT = "accept"
        REJECT = "reject"
        NEEDS_REVIEW = "needs_review"

## TODO: Get familiar with dataframe functions: apply, to_dict, group_by, to_csv, transform
## HH: Done
## TODO: Get familiar with accessing dataframe columns
## HH: Done

#File Names
INPUT_FILE = 'verdicts.json'
OUTPUT_JSON = 'flagged_verdicts_validation.json'
OUTPUT_CSV_DIR = 'data/validation'
OUTPUT_CSV = os.path.join(OUTPUT_CSV_DIR, 'verified_verdicts.csv')

# TODO: Refactor column names into top-level constants
# e.g., COL_COURSE_CODE = "code"
# course keys
COL_COURSE_CODE = "code"
COL_COURSE_TITLE = "title"
COL_SKILLS_LIST = "skills"
#Nested skill keys
COL_SKILL_NAME = "name"
COL_VERDICT_RESULT = "verdict"
COL_CONFIDENCE = "confidence"
COL_GUIDANCE = "guidance"
COL_SOURCE = "source"

# class ValidationFlag(Enum):
#     """TODO: Expand this Enum for all validation rules and use instead of strings"""
#     # "MIN_SKILLS_COUNT_VIOLATION" is the string value
#     MIN_SKILLS_COUNT = "MIN_SKILLS_COUNT_VIOLATION"
#     MISSING_ACTIVE_LISTENING = "SEMINAR_MISSING_ACTIVE_LISTENING"
#     MISSING_SPEAKING = "SEMINAR_MISSING_SPEAKING"
#     INVALID_VERDICT = "INVALID_VERDICT"
#     INVALID_CONFIDENCE = "INVALID_CONFIDENCE"
#     INVALID_COURSE_CODE = "INVALID_COURSE_CODE"
#     MISSING_COURSE_TITLE = "MISSING_COURSE_TITLE"

ValidationFlag.MIN_SKILLS_COUNT
ValidationFlag.MISSING_ACTIVE_LISTENING
ValidationFlag.MISSING_SPEAKING
ValidationFlag.INVALID_VERDICT
ValidationFlag.INVALID_CONFIDENCE
ValidationFlag.INVALID_COURSE_CODE
# ==============================================================================
# Validation Logic Placeholders
# TODO: Translate each function from test_pipeline.py and the Sprint Breakdown
# ==============================================================================

def validate_data_contract_shape(df):
    """TODO: Ensure JSON follows the required data contract."""
    """IMPORTANT:
        university, degree, tier, overview, etc. are TOP-LEVEL JSON fields.
        They are NOT columns in the flattened DataFrame.

        This fixes :
        KeyError: 'university'

        CSV columns:
        Skill Name
        Verdict
        Confidence
        Validation Flags
        Manual Action
        Reviewer Notes
    """

    
    # required_keys = {"source", "university", "degree", "tier", "courses", "overview"}
    # DataFrame only has these columns:
    # code, title, name, verdict, confidence, guidance, and source
    # CHECK THE NEXT TWO LINES: I am not sure!
    df["flag_missing_course_code"] = df["code"] == ""
    df["flag_missing_title"] = df["title"] == ""
    df["flag_missing_skill_name"] = df["name"] == ""
    # source, university, degree, tier, and overview are stored in shell, not in df

    # In test_pipeline.py: it also checks:
    # source -> major or upload
    # university -> Texas A&M University
    # tier -> verified or estimate

    # Meaning of the following lines:
    # Create a new column called flag_missing_source
    #If source is empty(""), it stores True, otherwise, False
    return df

def validate_courses_structure(df):
    """TODO: Validate course objects have required keys (code, title, skills)."""
    df["flag_missing_course_code"] = df["code"] == ""
    df["flag_missing_title"] = df["title"] == ""
    df["flag_missing_skills"] = df["skills"] == ""
    return df

def validate_overview_structure(df):
    """TODO: Validate overview statistics match internal data."""
    # Checks: automating, transforming, untouched, summary

    df["flag_missing_summary"] = df["summary"] == ""
    df["flag_invalid_automating"] = df["automating"] < 0
    # tests say that they must be >= 0
    df["flag_invalid_transforming"] = df["transforming"] < 0
    df["flag_invalid_untouched"] = df["untouched"] < 0
    return df

def validate_skill_verdicts(df):
    """TODO: Ensure all skills have an accepted verdict status."""
    # Valid verdicts: Automating, Transforming, Untouched
    # Valid confidence: high, medium, low
    #isin() asks "Is this value inside my list?"
    #~ means NOT, so it flips the answers. Only "wrong" is flagged!
    
    #valid_verdicts = ["Automating", "Transforming", "Untouched"]
    #valid_confidences = ["high", "medium", "low"]
    #TODO: Change into Enums
    # value() means "give me the actual value stored in the Enum"
    # class Verdict(Enum):
    #     AUTOMATING = "Automating"
    #     TRANSFORMING = "Transforming"
    #     UNTOUCHED = "Untouched"
    
    # class Confidence(Enum):
    #     HIGH = "high"
    #     MEDIUM = "medium"
    #     LOW = "low"

    valid_verdicts = [
        Verdict.AUTOMATING.value,
        Verdict.TRANSFORMING.value,
        Verdict.UNTOUCHED.value
    ]

    valid_confidences = [
        Confidence.HIGH.value,
        Confidence.MEDIUM.value,
        Confidence.LOW.value
    ]
# End of Enum TODO upbove - Haya

    df['flag_verdict'] = ~df['verdict'].isin(valid_verdicts) & df['name'].notna()
    df['flag_confidence'] = ~df['confidence'].isin(valid_confidences) & df['name'].notna()
    return df
    


def load_and_flatten_data(input_file):
    """Reads the JSON file and explodes nested skills into a flattened DataFrame."""
    with open(input_file, 'r') as f:
        data = json.load(f)

    # Preserve the top-level shell for our final JSON export
    # These columns are stored in "shell", not in "df"
    shell = {
        "source": data.get('source'),
        "university": data.get('university'),
        "degree": data.get('degree'),
        "tier": data.get('tier'),
        "overview": data.get('overview')
    }

    # Extract courses and explode the skills list
    df_courses = pd.DataFrame(data['courses'])
    df_exploded = df_courses.explode('skills').reset_index(drop=True)

    # Normalize nested skill dictionaries into discrete columns while preserving course metadata
    if not df_exploded['skills'].isnull().all():
        df_skills = pd.json_normalize(df_exploded['skills'].dropna())
        df_skills = df_skills.reindex(df_exploded.index)
    else:
        df_skills = pd.DataFrame(columns=['name', 'verdict', 'confidence', 'guidance', 'source'])

    # Final flattened dataframe ready for vectorized operations
    df = pd.concat([df_exploded[['code', 'title']], df_skills], axis=1)

    return df, shell


def check_minimum_skills(df):
    """Ensures each course has at least 3 skills mapped to it."""
    skill_counts = df.groupby('code')['name'].transform('count')
    df['flag_min_skills'] = skill_counts < 3
    return df


def check_seminar_rules(df):
    """Enforces specific active listening/speaking rules for seminars."""
    df['is_seminar'] = (
            df['title'].str.contains(r'(?i)seminar|special topics', na=False) |
            df['code'].str.contains(r'(?i)91\b|481\b|482\b', na=False)
    )

    # Broadcast presence of specific skills per course
    has_al = df.groupby('code')['name'].transform(lambda x: (x == 'Active Listening').any())
    has_sp = df.groupby('code')['name'].transform(lambda x: (x == 'Speaking').any())

    df['flag_seminar_al'] = df['is_seminar'] & ~has_al
    df['flag_seminar_sp'] = df['is_seminar'] & ~has_sp
    return df

# Below is something similar to TODO: validate_skill_verdicts().
# I will have check_valid_properties() call validate_skill_verdicts
def check_valid_properties(df):
    """Validates that skill properties match the accepted enum schemas."""
    return validate_skill_verdicts(df)


def add_validation_flags(df):
    """Aggregates individual flags into a unified array and string column."""

    def extract_flags(row):
        flags = []
        if row.get('flag_min_skills'): flags.append('MIN_SKILLS_COUNT_VIOLATION')
        if row.get('flag_seminar_al'): flags.append('SEMINAR_MISSING_ACTIVE_LISTENING')
        if row.get('flag_seminar_sp'): flags.append('SEMINAR_MISSING_SPEAKING')
        if row.get('flag_verdict'): flags.append('INVALID_VERDICT')
        if row.get('flag_confidence'): flags.append('INVALID_CONFIDENCE')
        if row.get('flag_missing_course_code') : flags.append('INVALID_COURSE_CODE')
        return flags

    df['validation_flags_list'] = df.apply(extract_flags, axis=1)
    df['Validation Flags'] = df['validation_flags_list'].apply(lambda x: ", ".join(x) if x else "NONE")
    return df


def rebuild_and_export(df, shell, json_out):
    """Vectorized reconstruction of the nested JSON and CSV export."""

    course_level_keywords = (
        "MIN_SKILLS_COUNT_VIOLATION", 
        "SEMINAR_MISSING_ACTIVE_LISTENING",
        "SEMINAR_MISSING_SPEAKING", 
        "INVALID_COURSE_CODE"
        )

    # Partition flags into skill-level and course-level arrays
    df['skill_flags'] = df['validation_flags_list'].apply(
        lambda flags: [{"type": f, "severity": "high", "details": f"Failed property rule: {f}"}
                       for f in flags if not any(kw in f for kw in course_level_keywords)]
    )
    df['course_flags'] = df['validation_flags_list'].apply(
        lambda flags: [f for f in flags if any(kw in f for kw in course_level_keywords)]
    )

    # Process valid skills mapping using dataframe apply to construct dictionaries
    valid_skills = df.dropna(subset=['name']).copy()
    valid_skills['guidance'] = valid_skills['guidance'].fillna("")
    valid_skills['source'] = valid_skills['source'].fillna("")

    def create_skill_dict(row):
        d = {
            "name": row['name'],
            "verdict": row['verdict'],
            "confidence": row['confidence'],
            "guidance": row['guidance'],
            "source": row['source']
        }
        if row['skill_flags']:
            d["error_flags"] = row['skill_flags']
        return d

    valid_skills['skill_dict'] = valid_skills.apply(create_skill_dict, axis=1)

    # Group up to the course level
    grouped = df.groupby('code', sort=False)

    courses_df = pd.DataFrame({
        'code': grouped['code'].first(),
        'title': grouped['title'].first(),
    })

    # Aggregate course flags (flatten list of lists and deduplicate)
    courses_df['course_flags_raw'] = grouped['course_flags'].apply(lambda x: list(set(sum(x, []))))
    courses_df['error_flags'] = courses_df['course_flags_raw'].apply(
        lambda flags: [{"type": f, "details": f"Failed structural schema: {f}"} for f in flags]
    )

    # Aggregate nested skill arrays
    course_skills_series = valid_skills.groupby('code', sort=False)['skill_dict'].apply(list)
    courses_df['skills'] = courses_df['code'].map(course_skills_series)
    courses_df['skills'] = courses_df['skills'].apply(lambda x: x if isinstance(x, list) else [])

    # Calculate validation status
    def determine_status(row):
        has_course_flags = len(row['error_flags']) > 0
        has_skill_flags = any('error_flags' in s for s in row['skills'])
        return "flagged" if has_course_flags or has_skill_flags else "passed"

    courses_df['validation_status'] = courses_df.apply(determine_status, axis=1)

    # Establish default manual review payload
    courses_df['review_status'] = courses_df.apply(
        lambda _: {
            "is_reviewed": False,
            "manual_action": ManualAction.UNREVIEWED.value,
            "reviewer_notes": ""
            },
            axis=1
    ) # TODO: these review statuses can be made into an enum

    #Enum:
    # class ManualAction(Enum):
    #     UNREVIEWED = "unreviewed"
    #     ACCEPT = "accept"
    #     REJECT = "reject"
    #     NEEDS_REVIEW = "needs_review"
    #

    # Restrict to final JSON payload schema and inject into the shell
    final_courses_df = courses_df[['code', 'title', 'validation_status', 'error_flags', 'review_status', 'skills']]
    shell['courses'] = final_courses_df.to_dict(orient='records')
    
    def _generate_validation_summary(courses_df):
        # FIXED ERROR: Pandas operations like .sum and .nuique do NOT return standard Python integers. Instead, they return NumPy integers.
        #SOLUTION: Wrapping the Pandas output in int converts NumPy integers into native Python int!!
        total_courses = int(courses_df["code"].nunique())
        # "code" contains course codes like: CSCE 111, CSCE 120,etc
        # nunique() counts DIFFERENT course codes
        courses_flagged = int((courses_df["validation_status"] == "flagged").sum())
        # counts the courses that are flagged
        #.sum() counts the True ones
        courses_passed = int((courses_df["validation_status"] == "passed").sum())
        # counts the courses that passed
        """
        TODO: Implement summary logic.
        Behavior:
        1. Calculate total number of unique courses (nunique).
        [final_courses_df (6 columns): code, title, validation_status, error_flags, review_status, and skills]
        2. Determine how many courses have one or more validation flags "flagged"
        3. Determine how many courses are clear "passed".
        4. Return a dictionary containing these three metrics.
        5. Pass courses_df into the function
        """
        return {
            "total_courses_processed": total_courses,
            "courses_flagged_for_manual_review": courses_flagged,
            "courses_passed_automated_review": courses_passed
        }
    #END OF FINAL TODO!!!

    # Inject summary metrics into the JSON shell
    #TODO question: Is it supposed to be "df" in the parenthesis or "courses_df"?
    shell['validation_summary'] = _generate_validation_summary(courses_df)

    # Save to the final output file
    with open(json_out, 'w') as f:
        json.dump(shell, f, indent=2)


def run_validation_pipeline():
    input_file = 'verdicts.json'
    json_out = 'flagged_verdicts_validation.json'

    print("1. Loading and flattening data...")
    df, shell = load_and_flatten_data(input_file)

    print("2. Running vectorized structural audits...")
    df = check_minimum_skills(df)
    df = check_seminar_rules(df)
    df = check_valid_properties(df)
    df = validate_data_contract_shape(df)
#converts it to csv

    df.to_csv("output.csv") # This line generates csv for sanity check

    print("3. Generating Validation Flags...")
    df = add_validation_flags(df)

    print("4. Formatting and exporting data...")
    rebuild_and_export(df, shell, json_out)

    print(f"✔ JSON validation output exported to {json_out}")


if __name__ == "__main__":
    run_validation_pipeline()
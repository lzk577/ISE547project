"""
Evaluation Metrics Calculator
Calculates code correctness, code quality, and performance metrics
"""
import ast
import time
import pandas as pd
import re
from typing import Dict, List, Optional
from datetime import datetime

def split_dataset(csv_filepath: str, num_splits: int = 3) -> List[str]:
    """
    Split CSV dataset into multiple parts for evaluation
    Returns list of file paths for split datasets
    """
    try:
        df = pd.read_csv(csv_filepath)
        total_rows = len(df)
        
        if total_rows < num_splits:
            # If dataset is too small, return original file
            return [csv_filepath]
        
        split_size = total_rows // num_splits
        splits = []
        
        for i in range(num_splits):
            start_idx = i * split_size
            if i == num_splits - 1:
                # Last split gets remaining rows
                end_idx = total_rows
            else:
                end_idx = (i + 1) * split_size
            
            split_df = df.iloc[start_idx:end_idx].copy()
            
            # Save split to temporary file
            split_filepath = csv_filepath.replace('.csv', f'_split_{i+1}.csv')
            split_df.to_csv(split_filepath, index=False)
            splits.append(split_filepath)
        
        return splits
    except Exception as e:
        print(f"Error splitting dataset: {e}")
        return [csv_filepath]

def check_syntax_correctness(code: str) -> Dict:
    """Check if code is syntactically correct"""
    try:
        ast.parse(code)
        return {
            'syntax_valid': True,
            'syntax_errors': []
        }
    except SyntaxError as e:
        return {
            'syntax_valid': False,
            'syntax_errors': [{
                'line': e.lineno,
                'message': str(e),
                'text': e.text
            }]
        }
    except Exception as e:
        return {
            'syntax_valid': False,
            'syntax_errors': [{'message': str(e)}]
        }

def check_code_quality(code: str) -> Dict:
    """Evaluate code quality metrics"""
    metrics = {
        'has_imports': False,
        'has_comments': False,
        'line_count': 0,
        'complexity_score': 0,
        'readability_score': 0
    }
    
    lines = code.split('\n')
    metrics['line_count'] = len([l for l in lines if l.strip()])
    
    # Check for imports
    if re.search(r'^import\s+|^from\s+.*\s+import', code, re.MULTILINE):
        metrics['has_imports'] = True
    
    # Check for comments
    if re.search(r'#.*', code):
        metrics['has_comments'] = True
    
    # Simple complexity score (based on control structures)
    complexity_keywords = ['if', 'elif', 'else', 'for', 'while', 'try', 'except', 'with']
    complexity_count = sum(1 for keyword in complexity_keywords if re.search(rf'\b{keyword}\b', code))
    metrics['complexity_score'] = complexity_count
    
    # Readability score (0-10)
    # Based on: line length, naming conventions, structure
    readability = 10
    long_lines = sum(1 for line in lines if len(line) > 100)
    if long_lines > len(lines) * 0.2:
        readability -= 2
    if not metrics['has_comments'] and metrics['line_count'] > 10:
        readability -= 1
    if metrics['complexity_score'] > 5:
        readability -= 1
    metrics['readability_score'] = max(0, readability)
    
    return metrics

def check_code_safety(code: str) -> Dict:
    """Check code safety (dangerous operations)"""
    dangerous_patterns = {
        'file_write': [r'\.to_csv\(', r'\.to_excel\(', r'open\(.*[\'"]w', r'\.write\('],
        'file_read': [r'open\(.*[\'"]r', r'pd\.read_'],
        'network': [r'requests\.', r'urllib\.', r'http\.'],
        'system': [r'os\.system', r'subprocess\.', r'exec\(', r'eval\('],
        'dangerous_imports': [r'import\s+os', r'import\s+subprocess', r'import\s+sys']
    }
    
    safety_issues = []
    for category, patterns in dangerous_patterns.items():
        for pattern in patterns:
            if re.search(pattern, code, re.IGNORECASE):
                safety_issues.append({
                    'category': category,
                    'pattern': pattern,
                    'severity': 'high' if category in ['system', 'network'] else 'medium'
                })
    
    return {
        'is_safe': len(safety_issues) == 0,
        'safety_issues': safety_issues,
        'safety_score': 1.0 if len(safety_issues) == 0 else max(0, 1.0 - len(safety_issues) * 0.2)
    }

def analyze_time_complexity(code: str) -> Dict:
    """
    Analyze time complexity of the code
    Returns complexity notation (O(1), O(n), O(n²), etc.)
    """
    complexity_score = 0
    complexity_notation = "O(1)"
    
    # Count loops and nested structures
    loop_patterns = [
        (r'\bfor\s+\w+\s+in\s+', 1),  # for loops
        (r'\bwhile\s+', 1),  # while loops
        (r'\.apply\(', 1),  # pandas apply
        (r'\.iterrows\(', 1),  # pandas iterrows
        (r'\.itertuples\(', 1),  # pandas itertuples
    ]
    
    nested_loops = 0
    for pattern, weight in loop_patterns:
        matches = len(re.findall(pattern, code, re.IGNORECASE))
        nested_loops += matches * weight
    
    # Check for pandas operations that affect complexity
    pandas_ops = {
        'O(1)': [r'\.head\(', r'\.tail\(', r'\.iloc\[', r'\.loc\[', r'\.shape', r'\.dtypes'],
        'O(n)': [r'\.mean\(', r'\.sum\(', r'\.count\(', r'\.unique\(', r'\.value_counts\(', 
                 r'\.groupby\(', r'\.sort_values\(', r'\.dropna\(', r'\.fillna\('],
        'O(n log n)': [r'\.sort_values\(', r'\.sort_index\('],
        'O(n²)': [r'\.merge\(', r'\.join\(', r'\.concat\(.*axis=1']
    }
    
    max_complexity = "O(1)"
    complexity_order = ["O(1)", "O(n)", "O(n log n)", "O(n²)", "O(n³)"]
    
    for complexity, patterns in pandas_ops.items():
        for pattern in patterns:
            if re.search(pattern, code, re.IGNORECASE):
                if complexity_order.index(complexity) > complexity_order.index(max_complexity):
                    max_complexity = complexity
    
    # Adjust based on nested loops
    if nested_loops > 0:
        if nested_loops == 1:
            if max_complexity == "O(1)":
                max_complexity = "O(n)"
            elif max_complexity == "O(n)":
                max_complexity = "O(n²)"
        elif nested_loops >= 2:
            if max_complexity == "O(1)":
                max_complexity = "O(n²)"
            elif max_complexity == "O(n)":
                max_complexity = "O(n²)"
            else:
                max_complexity = "O(n³)"
    
    complexity_notation = max_complexity
    
    # Calculate complexity score (lower is better, 0-1 scale)
    complexity_scores = {
        "O(1)": 1.0,
        "O(log n)": 0.9,
        "O(n)": 0.7,
        "O(n log n)": 0.5,
        "O(n²)": 0.3,
        "O(n³)": 0.1
    }
    complexity_score = complexity_scores.get(complexity_notation, 0.5)
    
    return {
        'notation': complexity_notation,
        'score': complexity_score,
        'nested_loops': nested_loops,
        'estimated_operations': nested_loops + 1
    }

def analyze_space_complexity(code: str, csv_file: str = None) -> Dict:
    """
    Analyze space complexity of the code
    Returns complexity notation and estimated memory usage
    """
    space_complexity = "O(1)"
    estimated_memory_mb = 0
    
    # Check for operations that create new data structures
    space_indicators = {
        'O(1)': [r'\.head\(', r'\.tail\(', r'\.iloc\[', r'\.loc\[', r'\.shape', r'\.dtypes'],
        'O(n)': [r'\.copy\(', r'\.drop\(', r'\.dropna\(', r'\.fillna\(', r'\.assign\(',
                 r'result\s*=', r'df_new\s*=', r'df_filtered\s*='],
        'O(n²)': [r'\.merge\(', r'\.join\(', r'\.concat\(', r'\.pivot\(', r'\.pivot_table\(']
    }
    
    complexity_order = ["O(1)", "O(n)", "O(n²)"]
    max_complexity = "O(1)"
    
    for complexity, patterns in space_indicators.items():
        for pattern in patterns:
            if re.search(pattern, code, re.IGNORECASE):
                if complexity_order.index(complexity) > complexity_order.index(max_complexity):
                    max_complexity = complexity
    
    space_complexity = max_complexity
    
    # Try to estimate memory if CSV file is available
    if csv_file:
        try:
            import os
            file_size = os.path.getsize(csv_file) / (1024 * 1024)  # MB
            # Rough estimate: space complexity affects memory multiplier
            multipliers = {"O(1)": 1.0, "O(n)": 2.0, "O(n²)": 4.0}
            estimated_memory_mb = file_size * multipliers.get(space_complexity, 2.0)
        except:
            pass
    
    # Calculate space score (lower is better, 0-1 scale)
    space_scores = {
        "O(1)": 1.0,
        "O(n)": 0.6,
        "O(n²)": 0.2
    }
    space_score = space_scores.get(space_complexity, 0.5)
    
    return {
        'notation': space_complexity,
        'score': space_score,
        'estimated_memory_mb': estimated_memory_mb
    }

def analyze_prompt_understanding(question: str, generated_code: str, csv_file: str = None) -> Dict:
    """
    Analyze Natural-Language Intent Accuracy
    Check if the model correctly understands the question:
    - Whether correct column names are extracted
    - Whether natural language descriptions are correctly parsed
    - Whether statistical requirements are correctly understood
    """
    score = 0.0
    max_score = 0.0
    details = {
        'column_extraction_score': 0.0,
        'nl_parsing_score': 0.0,
        'statistical_understanding_score': 0.0,
        'extracted_columns': [],
        'mentioned_columns': [],
        'statistical_operations': []
    }
    
    # Get available columns from CSV if available
    available_columns = []
    if csv_file:
        try:
            df = pd.read_csv(csv_file, nrows=0)  # Read only headers
            available_columns = [col.lower() for col in df.columns.tolist()]
            print(f"[PROMPT_UNDERSTANDING] Loaded {len(available_columns)} columns from CSV: {available_columns[:5]}...")
        except Exception as e:
            print(f"[PROMPT_UNDERSTANDING] Error loading CSV columns: {e}")
            pass
    else:
        print(f"[PROMPT_UNDERSTANDING] No CSV file provided")
    
    # 1. Column extraction analysis
    # Extract column names mentioned in question (case-insensitive)
    question_lower = question.lower()
    mentioned_in_question = []
    if available_columns:
        for col in available_columns:
            if col in question_lower or col.replace('_', ' ') in question_lower:
                mentioned_in_question.append(col)
        details['mentioned_columns'] = mentioned_in_question
    
    # Extract column names used in code
    # Pattern: df['column'], df["column"], df[['col1', 'col2']]
    # Exclude pandas methods (head, tail, mean, sum, etc.)
    pandas_methods = {'head', 'tail', 'mean', 'sum', 'max', 'min', 'count', 'size', 
                      'shape', 'dtypes', 'columns', 'index', 'values', 'copy', 'drop',
                      'fillna', 'dropna', 'groupby', 'sort_values', 'sort_index',
                      'nlargest', 'nsmallest', 'query', 'loc', 'iloc', 'apply', 'agg',
                      'merge', 'join', 'concat', 'pivot', 'pivot_table', 'describe',
                      'info', 'isnull', 'notnull', 'unique', 'value_counts', 'sample'}
    
    column_patterns = [
        r"df\[['\"]([^'\"]+)['\"]\]",  # df['column'] - single column access
        r"df\[\[['\"]([^'\"]+)['\"]",  # df[['column']] - list access start
    ]
    extracted_columns = set()
    for pattern in column_patterns:
        matches = re.findall(pattern, generated_code, re.IGNORECASE)
        for match in matches:
            if isinstance(match, str) and match.lower() not in pandas_methods:
                extracted_columns.add(match.lower())
    
    # Also handle df[['col1', 'col2']] pattern more carefully
    list_pattern = r"df\[\[([^\]]+)\]\]"
    list_matches = re.findall(list_pattern, generated_code, re.IGNORECASE)
    for match in list_matches:
        # Extract individual column names from list
        cols = re.findall(r"['\"]([^'\"]+)['\"]", match)
        for col in cols:
            if col.lower() not in pandas_methods:
                extracted_columns.add(col.lower())
    
    details['extracted_columns'] = list(extracted_columns)
    print(f"[PROMPT_UNDERSTANDING] Extracted columns from code: {details['extracted_columns']}")
    print(f"[PROMPT_UNDERSTANDING] Mentioned columns in question: {details['mentioned_columns']}")
    
    # Score column extraction (0-0.4)
    if mentioned_in_question:
        if extracted_columns:
            # Check if all mentioned columns are used
            matched = sum(1 for col in mentioned_in_question if col in extracted_columns)
            details['column_extraction_score'] = (matched / len(mentioned_in_question)) * 0.4
            print(f"[PROMPT_UNDERSTANDING] Column extraction: {matched}/{len(mentioned_in_question)} matched, score: {details['column_extraction_score']}")
        else:
            details['column_extraction_score'] = 0.0
            print(f"[PROMPT_UNDERSTANDING] Column extraction: No columns extracted from code, score: 0.0")
    else:
        # If no columns mentioned, give partial score if code uses columns
        if extracted_columns:
            details['column_extraction_score'] = 0.2
            print(f"[PROMPT_UNDERSTANDING] Column extraction: No columns mentioned, but code uses columns, score: 0.2")
        else:
            details['column_extraction_score'] = 0.1
            print(f"[PROMPT_UNDERSTANDING] Column extraction: No columns mentioned or used, score: 0.1")
    score += details['column_extraction_score']
    max_score += 0.4
    
    # 2. Natural language parsing analysis (0-0.3)
    # Check for common NL patterns and their code equivalents
    nl_patterns = {
        'top_n': {
            'question_patterns': [r'top\s+(\d+)', r'largest\s+(\d+)', r'biggest\s+(\d+)', r'highest\s+(\d+)'],
            'code_patterns': [r'\.nlargest\(', r'\.head\(', r'\.sort_values\(.*ascending\s*=\s*False'],
            'weight': 0.06
        },
        'first_n_rows': {
            'question_patterns': [r'first\s+(\d+)\s+rows?', r'first\s+(\d+)', r'extract.*first\s+(\d+)'],
            'code_patterns': [r'\.head\(', r'\.iloc\[.*:\s*\d+', r'\.loc\[.*:\s*\d+'],
            'weight': 0.06
        },
        'bottom_n': {
            'question_patterns': [r'bottom\s+(\d+)', r'smallest\s+(\d+)', r'lowest\s+(\d+)'],
            'code_patterns': [r'\.nsmallest\(', r'\.tail\(', r'\.sort_values\(.*ascending\s*=\s*True'],
            'weight': 0.06
        },
        'filtering': {
            'question_patterns': [r'where', r'filter', r'only', r'greater than', r'less than', r'equal to'],
            'code_patterns': [r'df\[.*\]', r'\.query\(', r'\.loc\[', r'\.iloc\['],
            'weight': 0.06
        },
        'visualization': {
            'question_patterns': [r'chart', r'graph', r'plot', r'visualize', r'bar chart', r'histogram', r'pie chart'],
            'code_patterns': [r'plt\.', r'matplotlib', r'seaborn', r'sns\.', r'\.plot\(', r'fig\s*=', r'ax\.'],
            'weight': 0.06
        }
    }
    
    nl_score = 0.0
    for pattern_name, pattern_info in nl_patterns.items():
        question_matches = any(re.search(p, question_lower) for p in pattern_info['question_patterns'])
        code_matches = any(re.search(p, generated_code, re.IGNORECASE) for p in pattern_info['code_patterns'])
        
        if question_matches and code_matches:
            nl_score += pattern_info['weight']
        elif question_matches and not code_matches:
            # Pattern mentioned but not implemented
            nl_score += pattern_info['weight'] * 0.3
    
    details['nl_parsing_score'] = nl_score
    score += nl_score
    max_score += 0.3
    print(f"[PROMPT_UNDERSTANDING] NL parsing score: {nl_score}")
    
    # 3. Statistical understanding analysis (0-0.3)
    # Check if statistical operations match the question
    stat_patterns = {
        'mean': {
            'question': [r'average', r'mean', r'avg'],
            'code': [r'\.mean\(', r'\.average\('],
            'weight': 0.1
        },
        'sum': {
            'question': [r'sum', r'total', r'add'],
            'code': [r'\.sum\(', r'\.agg\(.*sum'],
            'weight': 0.1
        },
        'max': {
            'question': [r'maximum', r'max', r'highest', r'largest'],
            'code': [r'\.max\(', r'\.agg\(.*max', r'\.nlargest\('],
            'weight': 0.1
        },
        'min': {
            'question': [r'minimum', r'min', r'lowest', r'smallest'],
            'code': [r'\.min\(', r'\.agg\(.*min', r'\.nsmallest\('],
            'weight': 0.1
        },
        'count': {
            'question': [r'count', r'number of', r'how many'],
            'code': [r'\.count\(', r'\.size\(', r'len\(', r'\.shape\[0\]'],
            'weight': 0.1
        },
        'groupby': {
            'question': [r'group by', r'by', r'per', r'for each'],
            'code': [r'\.groupby\(', r'\.pivot_table\('],
            'weight': 0.1
        }
    }
    
    stat_score = 0.0
    detected_stats = []
    for stat_name, stat_info in stat_patterns.items():
        question_matches = any(re.search(p, question_lower) for p in stat_info['question'])
        code_matches = any(re.search(p, generated_code, re.IGNORECASE) for p in stat_info['code'])
        
        if question_matches:
            detected_stats.append(stat_name)
            if code_matches:
                stat_score += stat_info['weight']
            else:
                # Mentioned but not implemented
                stat_score += stat_info['weight'] * 0.2
    
    details['statistical_operations'] = detected_stats
    details['statistical_understanding_score'] = stat_score
    score += stat_score
    max_score += 0.3
    print(f"[PROMPT_UNDERSTANDING] Statistical understanding score: {stat_score}, detected: {detected_stats}")
    
    # Normalize score to 0-1
    understanding_score = score / max_score if max_score > 0 else 0.0
    print(f"[PROMPT_UNDERSTANDING] Total score: {score}/{max_score} = {understanding_score}")
    
    return {
        'understanding_score': understanding_score,
        'details': details
    }

def analyze_requirement_coverage(question: str, generated_code: str) -> Dict:
    """
    Analyze Requirement Coverage
    Check if the code includes all requirements from the prompt:
    - Multiple filter conditions (are all conditions included?)
    - Multiple groupby columns (are all columns included?)
    - Sorting requirements (is sorting included if mentioned?)
    - Join conditions (are all join conditions included?)
    """
    score = 0.0
    max_score = 0.0
    details = {
        'filter_conditions_coverage': 1.0,
        'groupby_columns_coverage': 1.0,
        'sorting_coverage': 1.0,
        'join_conditions_coverage': 1.0,
        'missing_requirements': []
    }
    
    question_lower = question.lower()
    
    # 1. Filter conditions coverage
    # Count filter keywords in question
    filter_keywords = ['and', 'or', 'where', 'filter', 'greater than', 'less than', 
                      'equal to', 'not equal', 'contains', 'in', 'between']
    filter_count = sum(1 for keyword in filter_keywords if keyword in question_lower)
    
    # Count filter operations in code
    filter_ops = len(re.findall(r'df\[.*\]|\.query\(|\.loc\[.*\]|\.iloc\[.*\]', generated_code))
    
    if filter_count > 1:  # Multiple conditions mentioned
        if filter_ops >= filter_count:
            details['filter_conditions_coverage'] = 1.0
        else:
            details['filter_conditions_coverage'] = filter_ops / filter_count
            details['missing_requirements'].append(f'Missing {filter_count - filter_ops} filter condition(s)')
        score += details['filter_conditions_coverage'] * 0.3
    else:
        score += 0.3  # No multiple filters required
    max_score += 0.3
    
    # 2. Groupby columns coverage
    # Check for "group by X, Y, Z" patterns
    groupby_patterns = [
        r'group\s+by\s+([^,]+(?:,\s*[^,]+)+)',  # "group by A, B, C"
        r'by\s+([^,]+(?:,\s*[^,]+)+)',  # "by A, B, C"
    ]
    
    groupby_columns_mentioned = []
    for pattern in groupby_patterns:
        matches = re.findall(pattern, question_lower)
        for match in matches:
            columns = [col.strip() for col in match.split(',')]
            groupby_columns_mentioned.extend(columns)
    
    if groupby_columns_mentioned:
        # Count groupby columns in code
        groupby_match = re.search(r'\.groupby\(\[?([^\]]+)\]?\)', generated_code, re.IGNORECASE)
        if groupby_match:
            groupby_cols_in_code = [col.strip().strip("'\"") for col in groupby_match.group(1).split(',')]
            matched = sum(1 for col in groupby_columns_mentioned if any(col.lower() in gc.lower() for gc in groupby_cols_in_code))
            details['groupby_columns_coverage'] = matched / len(groupby_columns_mentioned) if groupby_columns_mentioned else 1.0
            if details['groupby_columns_coverage'] < 1.0:
                details['missing_requirements'].append(f'Missing {len(groupby_columns_mentioned) - matched} groupby column(s)')
        else:
            details['groupby_columns_coverage'] = 0.0
            details['missing_requirements'].append('Groupby operation missing')
        score += details['groupby_columns_coverage'] * 0.3
    else:
        # Check if groupby is used when not needed (false positive)
        if re.search(r'\.groupby\(', generated_code, re.IGNORECASE):
            score += 0.3  # Groupby present
        else:
            score += 0.3  # No groupby needed
    max_score += 0.3
    
    # 3. Sorting coverage
    sort_keywords = ['sort', 'order', 'ascending', 'descending', 'top', 'bottom', 'largest', 'smallest']
    sort_mentioned = any(keyword in question_lower for keyword in sort_keywords)
    
    if sort_mentioned:
        sort_in_code = bool(re.search(r'\.sort_values\(|\.sort_index\(|\.nlargest\(|\.nsmallest\(', generated_code, re.IGNORECASE))
        details['sorting_coverage'] = 1.0 if sort_in_code else 0.0
        if not sort_in_code:
            details['missing_requirements'].append('Sorting operation missing')
        score += details['sorting_coverage'] * 0.2
    else:
        score += 0.2  # No sorting required
    max_score += 0.2
    
    # 4. Join conditions coverage
    join_keywords = ['join', 'merge', 'combine', 'match']
    join_mentioned = any(keyword in question_lower for keyword in join_keywords)
    
    if join_mentioned:
        join_in_code = bool(re.search(r'\.merge\(|\.join\(|\.concat\(', generated_code, re.IGNORECASE))
        details['join_conditions_coverage'] = 1.0 if join_in_code else 0.0
        if not join_in_code:
            details['missing_requirements'].append('Join/merge operation missing')
        score += details['join_conditions_coverage'] * 0.2
    else:
        score += 0.2  # No join required
    max_score += 0.2
    
    # Coverage score (0-1)
    coverage_score = score / max_score if max_score > 0 else 1.0
    
    return {
        'coverage_score': coverage_score,
        'details': details
    }

def analyze_error_recovery(execution_result: Dict, recovery_attempts: List[Dict] = None) -> Dict:
    """
    Analyze Error Recovery Ability
    When code execution fails, evaluate:
    - Recovery Attempts Count
    - Recovery Success Rate
    - Error Fix Quality (whether the root cause is addressed)
    """
    if recovery_attempts is None:
        recovery_attempts = []
    
    has_error = execution_result.get('type') == 'error'
    error_message = execution_result.get('data', '') if has_error else None
    
    recovery_metrics = {
        'has_error': has_error,
        'error_message': error_message,
        'recovery_attempts_count': len(recovery_attempts),
        'recovery_success': False,
        'recovery_success_rate': 0.0,
        'error_fix_quality': 0.0,
        'recovery_details': []
    }
    
    if not has_error:
        # No error, perfect recovery score
        recovery_metrics['recovery_success'] = True
        recovery_metrics['recovery_success_rate'] = 1.0
        recovery_metrics['error_fix_quality'] = 1.0
        recovery_metrics['recovery_score'] = 1.0
        return recovery_metrics
    
    # Analyze recovery attempts
    if recovery_attempts:
        successful_recoveries = sum(1 for attempt in recovery_attempts 
                                   if attempt.get('success', False))
        recovery_metrics['recovery_success_rate'] = successful_recoveries / len(recovery_attempts) if recovery_attempts else 0.0
        recovery_metrics['recovery_success'] = successful_recoveries > 0
        
        # Analyze error fix quality
        # Check if errors were properly addressed
        fix_quality_scores = []
        for attempt in recovery_attempts:
            attempt_code = attempt.get('code', '')
            attempt_error = attempt.get('error', '')
            attempt_success = attempt.get('success', False)
            
            if attempt_success:
                # Successful recovery gets full score
                fix_quality_scores.append(1.0)
            else:
                # Check if error type changed (indicates progress)
                original_error_type = _classify_error(error_message)
                new_error_type = _classify_error(attempt_error)
                
                if original_error_type != new_error_type:
                    # Error type changed, partial progress
                    fix_quality_scores.append(0.5)
                else:
                    # Same error type, no progress
                    fix_quality_scores.append(0.1)
            
            recovery_metrics['recovery_details'].append({
                'attempt_number': len(recovery_metrics['recovery_details']) + 1,
                'success': attempt_success,
                'error': attempt_error,
                'fix_quality': fix_quality_scores[-1] if fix_quality_scores else 0.0
            })
        
        recovery_metrics['error_fix_quality'] = sum(fix_quality_scores) / len(fix_quality_scores) if fix_quality_scores else 0.0
    else:
        # No recovery attempts made
        recovery_metrics['recovery_success_rate'] = 0.0
        recovery_metrics['error_fix_quality'] = 0.0
    
    # Calculate overall recovery score
    # Weight: success rate 50%, fix quality 30%, attempts made 20%
    if recovery_attempts:
        recovery_metrics['recovery_score'] = (
            recovery_metrics['recovery_success_rate'] * 0.5 +
            recovery_metrics['error_fix_quality'] * 0.3 +
            (min(len(recovery_attempts) / 3.0, 1.0)) * 0.2  # Normalize attempts (max 3)
        )
    else:
        # No recovery attempts = 0 score
        recovery_metrics['recovery_score'] = 0.0
    
    return recovery_metrics

def _classify_error(error_message: str) -> str:
    """Classify error type for comparison"""
    if not error_message:
        return 'unknown'
    
    error_lower = error_message.lower()
    
    if 'keyerror' in error_lower or 'column' in error_lower:
        return 'column_error'
    elif 'syntax' in error_lower or 'invalid' in error_lower:
        return 'syntax_error'
    elif 'type' in error_lower or 'dtype' in error_lower:
        return 'type_error'
    elif 'index' in error_lower or 'out of range' in error_lower:
        return 'index_error'
    elif 'attribute' in error_lower or 'has no attribute' in error_lower:
        return 'attribute_error'
    elif 'value' in error_lower:
        return 'value_error'
    else:
        return 'other_error'

def calculate_evaluation_metrics(question: str, generated_code: str, 
                                 execution_result: Dict, csv_file: str, 
                                 model: str, execution_time: float = None,
                                 recovery_attempts: List[Dict] = None) -> Dict:
    """
    Calculate comprehensive evaluation metrics:
    1. Code Correctness
    2. Code Quality
    3. Performance Metrics
    """
    metrics = {
        'timestamp': datetime.now().isoformat(),
        'model': model,
        'question': question,
        'csv_file': csv_file
    }
    
    # 1. Code Correctness Metrics
    syntax_check = check_syntax_correctness(generated_code)
    execution_success = execution_result.get('type') != 'error'
    
    correctness_metrics = {
        'syntax_valid': syntax_check['syntax_valid'],
        'syntax_errors': syntax_check.get('syntax_errors', []),
        'execution_success': execution_success,
        'execution_error': execution_result.get('data') if not execution_success else None,
        'correctness_score': 0.0
    }
    
    # Calculate correctness score (0-1)
    if syntax_check['syntax_valid']:
        correctness_metrics['correctness_score'] += 0.5
    if execution_success:
        correctness_metrics['correctness_score'] += 0.5
    
    metrics['code_correctness'] = correctness_metrics
    
    # 2. Code Quality Metrics
    quality_metrics = check_code_quality(generated_code)
    safety_metrics = check_code_safety(generated_code)
    
    quality_metrics.update({
        'safety': safety_metrics,
        'quality_score': 0.0
    })
    
    # Calculate quality score (0-1)
    # Syntax: 30%, Safety: 30%, Readability: 20%, Structure: 20%
    if syntax_check['syntax_valid']:
        quality_metrics['quality_score'] += 0.3
    quality_metrics['quality_score'] += safety_metrics['safety_score'] * 0.3
    quality_metrics['quality_score'] += quality_metrics['readability_score'] / 10 * 0.2
    if quality_metrics['has_imports'] and quality_metrics['line_count'] > 0:
        quality_metrics['quality_score'] += 0.2
    
    metrics['code_quality'] = quality_metrics
    
    # 3. Performance Metrics
    # Analyze time and space complexity
    time_complexity = analyze_time_complexity(generated_code)
    space_complexity = analyze_space_complexity(generated_code, csv_file)
    
    performance_metrics = {
        'code_length': len(generated_code),
        'estimated_complexity': quality_metrics['complexity_score'],
        'line_count': quality_metrics['line_count'],
        'execution_time_seconds': execution_time if execution_time is not None else None,
        'execution_time_ms': (execution_time * 1000) if execution_time is not None else None,
        'time_complexity': time_complexity,
        'space_complexity': space_complexity,
        'performance_score': 0.0
    }
    
    # Calculate performance score (0-1)
    # Based on code efficiency indicators
    # Execution time: 30%, Time complexity: 30%, Space complexity: 20%, Code length: 10%, Execution success: 10%
    
    # Execution time score (lower is better)
    if execution_time is not None:
        if execution_time < 0.1:
            performance_metrics['performance_score'] += 0.3
        elif execution_time < 1.0:
            performance_metrics['performance_score'] += 0.25
        elif execution_time < 5.0:
            performance_metrics['performance_score'] += 0.15
        else:
            performance_metrics['performance_score'] += 0.05
    else:
        # If no execution time, use code length as proxy
        if performance_metrics['code_length'] < 500:
            performance_metrics['performance_score'] += 0.2
        elif performance_metrics['code_length'] < 1000:
            performance_metrics['performance_score'] += 0.15
        else:
            performance_metrics['performance_score'] += 0.1
    
    # Time complexity score
    performance_metrics['performance_score'] += time_complexity['score'] * 0.3
    
    # Space complexity score
    performance_metrics['performance_score'] += space_complexity['score'] * 0.2
    
    # Code length score
    if performance_metrics['code_length'] < 500:
        performance_metrics['performance_score'] += 0.1
    elif performance_metrics['code_length'] < 1000:
        performance_metrics['performance_score'] += 0.05
    
    # Execution success
    if execution_success:
        performance_metrics['performance_score'] += 0.1
    
    metrics['performance'] = performance_metrics
    
    # 4. Prompt Understanding Metrics (Natural-Language Intent Accuracy)
    prompt_understanding = analyze_prompt_understanding(question, generated_code, csv_file)
    metrics['prompt_understanding'] = prompt_understanding
    
    # 5. Requirement Coverage Metrics
    requirement_coverage = analyze_requirement_coverage(question, generated_code)
    metrics['requirement_coverage'] = requirement_coverage
    
    # 6. Error Recovery Metrics
    error_recovery = analyze_error_recovery(execution_result, recovery_attempts)
    metrics['error_recovery'] = error_recovery
    
    # Overall score (updated weights to include new metrics)
    # Original metrics: 60% (Correctness 25%, Quality 20%, Performance 15%)
    # New metrics: 40% (Understanding 15%, Coverage 15%, Recovery 10%)
    metrics['overall_score'] = (
        correctness_metrics['correctness_score'] * 0.25 +
        quality_metrics['quality_score'] * 0.20 +
        performance_metrics['performance_score'] * 0.15 +
        prompt_understanding['understanding_score'] * 0.15 +
        requirement_coverage['coverage_score'] * 0.15 +
        error_recovery['recovery_score'] * 0.10
    )
    
    return metrics

def save_evaluation_metrics(session_id: str, metrics: Dict, session_dir: str = None):
    """
    Save evaluation metrics to session directory
    Each session's metrics are stored in chat_history/{session_id}/metrics.json
    """
    import os
    import json
    
    # Determine session directory
    if session_dir is None:
        session_dir = os.path.join('chat_history', session_id)
    
    # Ensure session directory exists
    os.makedirs(session_dir, exist_ok=True)
    
    # Metrics file path
    metrics_file = os.path.join(session_dir, 'metrics.json')
    
    # Load existing metrics or create new list
    metrics_list = []
    if os.path.exists(metrics_file):
        try:
            with open(metrics_file, 'r', encoding='utf-8') as f:
                metrics_list = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Could not load existing metrics file: {e}. Creating new file.")
            metrics_list = []
    
    # Append new metrics to the list
    metrics_list.append(metrics)
    
    # Save updated metrics list
    try:
        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(metrics_list, f, ensure_ascii=False, indent=2)
        print(f"[METRICS] Evaluation metrics saved to {metrics_file} (Total: {len(metrics_list)} entries)")
    except IOError as e:
        print(f"[METRICS ERROR] Error saving metrics to {metrics_file}: {e}")
        import traceback
        print(f"[METRICS ERROR] Traceback: {traceback.format_exc()}")
    
    # Also maintain a summary file for quick access
    summary_file = os.path.join(session_dir, 'metrics_summary.json')
    
    # Calculate averages for execution time
    execution_times = [m.get('performance', {}).get('execution_time_seconds') 
                      for m in metrics_list 
                      if m.get('performance', {}).get('execution_time_seconds') is not None]
    avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else None
    
    # Collect time and space complexity notations
    time_complexities = [m.get('performance', {}).get('time_complexity', {}).get('notation', 'O(1)') 
                        for m in metrics_list]
    space_complexities = [m.get('performance', {}).get('space_complexity', {}).get('notation', 'O(1)') 
                         for m in metrics_list]
    
    # Calculate averages for new metrics
    understanding_scores = [m.get('prompt_understanding', {}).get('understanding_score', 0) 
                           for m in metrics_list]
    coverage_scores = [m.get('requirement_coverage', {}).get('coverage_score', 0) 
                      for m in metrics_list]
    recovery_scores = [m.get('error_recovery', {}).get('recovery_score', 0) 
                      for m in metrics_list]
    
    # Calculate recovery statistics
    total_recovery_attempts = sum(m.get('error_recovery', {}).get('recovery_attempts_count', 0) 
                                  for m in metrics_list)
    successful_recoveries = sum(1 for m in metrics_list 
                               if m.get('error_recovery', {}).get('recovery_success', False))
    errors_encountered = sum(1 for m in metrics_list 
                            if m.get('error_recovery', {}).get('has_error', False))
    
    summary_data = {
        'session_id': session_id,
        'total_entries': len(metrics_list),
        'last_updated': datetime.now().isoformat(),
        'summary': {
            'average_overall_score': sum(m.get('overall_score', 0) for m in metrics_list) / len(metrics_list) if metrics_list else 0,
            'average_correctness_score': sum(m.get('code_correctness', {}).get('correctness_score', 0) for m in metrics_list) / len(metrics_list) if metrics_list else 0,
            'average_quality_score': sum(m.get('code_quality', {}).get('quality_score', 0) for m in metrics_list) / len(metrics_list) if metrics_list else 0,
            'average_performance_score': sum(m.get('performance', {}).get('performance_score', 0) for m in metrics_list) / len(metrics_list) if metrics_list else 0,
            'average_understanding_score': sum(understanding_scores) / len(understanding_scores) if understanding_scores else 0,
            'average_coverage_score': sum(coverage_scores) / len(coverage_scores) if coverage_scores else 0,
            'average_recovery_score': sum(recovery_scores) / len(recovery_scores) if recovery_scores else 0,
            'average_execution_time_seconds': avg_execution_time,
            'average_execution_time_ms': (avg_execution_time * 1000) if avg_execution_time else None,
            'models_used': list(set(m.get('model', 'unknown') for m in metrics_list)),
            'total_questions': len(metrics_list),
            'successful_executions': sum(1 for m in metrics_list if m.get('code_correctness', {}).get('execution_success', False)),
            'errors_encountered': errors_encountered,
            'total_recovery_attempts': total_recovery_attempts,
            'successful_recoveries': successful_recoveries,
            'recovery_success_rate': (successful_recoveries / errors_encountered) if errors_encountered > 0 else 0.0,
            'time_complexity_distribution': {
                complexity: time_complexities.count(complexity) 
                for complexity in set(time_complexities)
            },
            'space_complexity_distribution': {
                complexity: space_complexities.count(complexity) 
                for complexity in set(space_complexities)
            }
        }
    }
    
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)
        print(f"[METRICS] Metrics summary saved to {summary_file}")
    except IOError as e:
        print(f"[METRICS ERROR] Error saving metrics summary: {e}")
        import traceback
        print(f"[METRICS ERROR] Traceback: {traceback.format_exc()}")


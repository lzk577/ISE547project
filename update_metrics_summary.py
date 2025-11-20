"""
Script to update or create metrics_summary.json for all sessions
This ensures all sessions have the latest metrics summary format
"""
import os
import json
from datetime import datetime
from evaluation_metrics import save_evaluation_metrics

def update_all_metrics_summaries():
    """Update metrics_summary.json for all sessions that have metrics.json"""
    chat_history_dir = 'chat_history'
    
    if not os.path.exists(chat_history_dir):
        print(f"Directory {chat_history_dir} does not exist!")
        return
    
    sessions_updated = 0
    sessions_skipped = 0
    sessions_error = 0
    
    # Iterate through all session directories
    for session_id in os.listdir(chat_history_dir):
        session_dir = os.path.join(chat_history_dir, session_id)
        
        # Skip if not a directory
        if not os.path.isdir(session_dir):
            continue
        
        metrics_file = os.path.join(session_dir, 'metrics.json')
        summary_file = os.path.join(session_dir, 'metrics_summary.json')
        
        # Check if metrics.json exists
        if not os.path.exists(metrics_file):
            print(f"Session {session_id}: No metrics.json found, skipping...")
            sessions_skipped += 1
            continue
        
        try:
            # Load existing metrics
            with open(metrics_file, 'r', encoding='utf-8') as f:
                metrics_list = json.load(f)
            
            if not isinstance(metrics_list, list) or len(metrics_list) == 0:
                print(f"Session {session_id}: metrics.json is empty or invalid, skipping...")
                sessions_skipped += 1
                continue
            
            # Calculate summary statistics
            execution_times = [m.get('performance', {}).get('execution_time_seconds') 
                              for m in metrics_list 
                              if m.get('performance', {}).get('execution_time_seconds') is not None]
            avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else None
            
            # Collect time and space complexity notations
            time_complexities = [m.get('performance', {}).get('time_complexity', {}).get('notation', 'O(1)') 
                                for m in metrics_list]
            space_complexities = [m.get('performance', {}).get('space_complexity', {}).get('notation', 'O(1)') 
                                 for m in metrics_list]
            
            # Calculate averages for new metrics (with fallback for old metrics)
            understanding_scores = [m.get('prompt_understanding', {}).get('understanding_score', 0) 
                                   for m in metrics_list 
                                   if 'prompt_understanding' in m]
            coverage_scores = [m.get('requirement_coverage', {}).get('coverage_score', 0) 
                              for m in metrics_list 
                              if 'requirement_coverage' in m]
            recovery_scores = [m.get('error_recovery', {}).get('recovery_score', 0) 
                              for m in metrics_list 
                              if 'error_recovery' in m]
            
            # Calculate recovery statistics
            total_recovery_attempts = sum(m.get('error_recovery', {}).get('recovery_attempts_count', 0) 
                                          for m in metrics_list 
                                          if 'error_recovery' in m)
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
            
            # Save summary file
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, ensure_ascii=False, indent=2)
            
            print(f"[OK] Session {session_id}: Updated metrics_summary.json ({len(metrics_list)} entries)")
            sessions_updated += 1
            
        except Exception as e:
            print(f"[ERROR] Session {session_id}: Error updating summary - {e}")
            sessions_error += 1
    
    print(f"\n=== Summary ===")
    print(f"Updated: {sessions_updated}")
    print(f"Skipped: {sessions_skipped}")
    print(f"Errors: {sessions_error}")

if __name__ == '__main__':
    print("Updating metrics_summary.json for all sessions...")
    print("=" * 50)
    update_all_metrics_summaries()
    print("=" * 50)
    print("Done!")


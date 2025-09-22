#!/usr/bin/env python3
import os
import re
import sys

def update_imports_in_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Pattern để tìm các câu lệnh import
    patterns = [
        # from src.analyzer import X
        (r'from\s+requirement_analyzer(\.[\w\.]+)?\s+import', r'from src.analyzer\1 import'),
        # import src.analyzer
        (r'import\s+requirement_analyzer(\s+as\s+[\w_]+)?', r'import src.analyzer\1'),
        # from src.models.multi_model import X
        (r'from\s+multi_model_integration(\.[\w\.]+)?\s+import', r'from src.models.multi_model\1 import'),
        # import src.models.multi_model
        (r'import\s+multi_model_integration(\s+as\s+[\w_]+)?', r'import src.models.multi_model\1'),
        # from src.models.cocomo.cocomo_ii_predictor import X
        (r'from\s+cocomo_ii_predictor\s+import', r'from src.models.cocomo.cocomo_ii_predictor import'),
        # import src.models.cocomo.cocomo_ii_predictor
        (r'import\s+cocomo_ii_predictor', r'import src.models.cocomo.cocomo_ii_predictor'),
        # from src.models.cocomo.cocomo_ii_api import X
        (r'from\s+cocomo_ii_api\s+import', r'from src.models.cocomo.cocomo_ii_api import'),
        # import src.models.cocomo.cocomo_ii_api
        (r'import\s+cocomo_ii_api', r'import src.models.cocomo.cocomo_ii_api'),
        # from src.feedback.feedback_api import X
        (r'from\s+feedback_api\s+import', r'from src.feedback.feedback_api import'),
        # import src.feedback.feedback_api
        (r'import\s+feedback_api', r'import src.feedback.feedback_api'),
        # from src.feedback.feedback_collector import X
        (r'from\s+feedback_collector\s+import', r'from src.feedback.feedback_collector import'),
        # import src.feedback.feedback_collector
        (r'import\s+feedback_collector', r'import src.feedback.feedback_collector'),
        # from src.feedback.feedback_feature_extractor import X
        (r'from\s+feedback_feature_extractor\s+import', r'from src.feedback.feedback_feature_extractor import'),
        # import src.feedback.feedback_feature_extractor
        (r'import\s+feedback_feature_extractor', r'import src.feedback.feedback_feature_extractor'),
        # from src.models.ml_models.model_retrainer import X
        (r'from\s+model_retrainer\s+import', r'from src.models.ml_models.model_retrainer import'),
        # import src.models.ml_models.model_retrainer
        (r'import\s+model_retrainer', r'import src.models.ml_models.model_retrainer'),
    ]

    updated_content = content
    changes_made = False
    
    for pattern, replacement in patterns:
        new_content = re.sub(pattern, replacement, updated_content)
        if new_content != updated_content:
            changes_made = True
            updated_content = new_content
    
    if changes_made:
        print(f"Updating imports in {file_path}")
        with open(file_path, 'w') as file:
            file.write(updated_content)
        return True
    
    return False

def process_directory(directory):
    updated_files = 0
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                if update_imports_in_file(file_path):
                    updated_files += 1
    
    return updated_files

if __name__ == '__main__':
    base_dir = '/workspaces/AI-Project'
    src_dir = os.path.join(base_dir, 'src')
    tests_dir = os.path.join(base_dir, 'tests')
    scripts_dir = os.path.join(base_dir, 'scripts')
    
    updated_files = 0
    updated_files += process_directory(src_dir)
    updated_files += process_directory(tests_dir)
    updated_files += process_directory(scripts_dir)
    
    print(f"Updated imports in {updated_files} files.")
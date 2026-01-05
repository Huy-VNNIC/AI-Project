"""
Comprehensive software effort estimation service
"""

import os
import json
import logging
import pandas as pd
import numpy as np
from ml_requirement_analyzer import MLRequirementAnalyzer
from model_integration import ModelSelector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("effort_estimation_service.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("EffortEstimationService")

class EffortEstimationService:
    """
    Service for estimating software development effort based on requirements
    """
    
    def __init__(self, models_dir='models'):
        """
        Initialize the effort estimation service
        
        Args:
            models_dir (str): Directory containing trained models
        """
        logger.info("Initializing Effort Estimation Service")
        
        # Initialize the requirement analyzer
        try:
            self.analyzer = MLRequirementAnalyzer()
            logger.info("ML Requirement Analyzer initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing ML Requirement Analyzer: {e}")
            raise
        
        # Initialize the model selector
        try:
            self.model_selector = ModelSelector(models_dir)
            logger.info("Model Selector initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Model Selector: {e}")
            raise
        
        # Conversion factors for different effort units
        self.effort_units = {
            'person_hours': 1,
            'person_days': 8,        # 1 day = 8 hours
            'person_weeks': 40,      # 1 week = 40 hours
            'person_months': 160,    # 1 month = 160 hours
            'person_years': 1920     # 1 year = 1920 hours
        }
    
    def estimate_effort(self, requirements_text, estimation_method='auto', unit='person_months'):
        """
        Estimate development effort based on requirements text
        
        Args:
            requirements_text (str): Requirements document text
            estimation_method (str): Method to use for estimation ('auto', 'cocomo', 'function_points', 'use_case_points', 'ml', 'ensemble')
            unit (str): Effort unit for output ('person_hours', 'person_days', 'person_weeks', 'person_months', 'person_years')
            
        Returns:
            dict: Effort estimation results
        """
        logger.info(f"Estimating effort using {estimation_method} method")
        
        try:
            # Analyze requirements
            analysis = self.analyzer.analyze_requirements_document(requirements_text)
            logger.info(f"Requirements analysis completed: {len(analysis['requirements'])} requirements identified")
            
            # Get ML features
            ml_features = analysis['ml_features']
            
            # Get effort estimation based on specified method
            if estimation_method == 'auto':
                # Use the best model as determined by the model selector
                model_name = self.model_selector.select_best_model(ml_features)
                effort = self.model_selector.predict(ml_features, model_name)
                method_used = f"ml_{model_name}"
            
            elif estimation_method == 'cocomo':
                # Use COCOMO II model
                cocomo_params = analysis['effort_estimation_parameters']['cocomo']
                effort = self._calculate_cocomo_effort(cocomo_params)
                method_used = 'cocomo'
            
            elif estimation_method == 'function_points':
                # Use Function Points Analysis
                fp_params = analysis['effort_estimation_parameters']['function_points']
                effort = self._calculate_fp_effort(fp_params)
                method_used = 'function_points'
            
            elif estimation_method == 'use_case_points':
                # Use Use Case Points
                ucp_params = analysis['effort_estimation_parameters']['use_case_points']
                effort = self._calculate_ucp_effort(ucp_params)
                method_used = 'use_case_points'
            
            elif estimation_method == 'ml':
                # Use ML model (default to random forest)
                effort = self.model_selector.predict(ml_features, 'random_forest')
                method_used = 'ml_random_forest'
            
            elif estimation_method == 'ensemble':
                # Use ensemble of all models
                effort = self.model_selector.get_ensemble_prediction(ml_features)
                method_used = 'ml_ensemble'
            
            else:
                raise ValueError(f"Unknown estimation method: {estimation_method}")
            
            # Convert effort to requested unit
            effort_in_hours = effort * self.effort_units.get('person_months', 160)  # Default to person-months
            effort_in_requested_unit = effort_in_hours / self.effort_units.get(unit, 160)
            
            # Get all model predictions for comparison
            all_predictions = {}
            try:
                all_ml_predictions = self.model_selector.predict_all_models(ml_features)
                for model_name, pred in all_ml_predictions.items():
                    if pred is not None:
                        all_predictions[f'ml_{model_name}'] = round(pred, 2)
            except Exception as e:
                logger.warning(f"Error getting all ML predictions: {e}")
            
            # Add traditional methods
            try:
                cocomo_params = analysis['effort_estimation_parameters']['cocomo']
                all_predictions['cocomo'] = round(self._calculate_cocomo_effort(cocomo_params), 2)
            except:
                pass
                
            try:
                fp_params = analysis['effort_estimation_parameters']['function_points']
                all_predictions['function_points'] = round(self._calculate_fp_effort(fp_params), 2)
            except:
                pass
                
            try:
                ucp_params = analysis['effort_estimation_parameters']['use_case_points']
                all_predictions['use_case_points'] = round(self._calculate_ucp_effort(ucp_params), 2)
            except:
                pass
            
            # Prepare result
            result = {
                'effort': round(effort_in_requested_unit, 2),
                'unit': unit,
                'method_used': method_used,
                'all_predictions': all_predictions,
                'requirements_summary': {
                    'total_requirements': analysis['summary']['total_requirements'],
                    'functional_requirements': analysis['summary']['by_type'].get('functional', 0),
                    'non_functional_requirements': sum(count for req_type, count in analysis['summary']['by_type'].items() if req_type != 'functional'),
                    'avg_complexity': round(analysis['summary']['avg_complexity'], 2),
                    'size_estimate_kloc': round(analysis['summary']['size_estimate_kloc'], 2),
                    'technologies_detected': analysis['summary']['technologies_detected']
                }
            }
            
            logger.info(f"Effort estimation completed: {result['effort']} {unit}")
            return result
            
        except Exception as e:
            logger.error(f"Error in effort estimation: {e}")
            raise
    
    def _calculate_cocomo_effort(self, cocomo_params):
        """
        Calculate effort using COCOMO II model
        
        Args:
            cocomo_params (dict): COCOMO II parameters
            
        Returns:
            float: Effort in person-months
        """
        # Extract parameters
        size = cocomo_params.get('size', 0)
        if size <= 0:
            size = 1  # Minimum size to avoid zero or negative values
        
        # Scale factors
        sf_sum = 0
        scale_factors = [
            cocomo_params.get('reliability', 1.0),
            cocomo_params.get('complexity', 1.0),
            cocomo_params.get('documentation', 1.0),
            cocomo_params.get('time_constraint', 1.0),
            cocomo_params.get('platform_volatility', 1.0)
        ]
        
        for sf in scale_factors:
            sf_sum += sf
        
        # Effort multipliers
        em_product = 1.0
        effort_multipliers = [
            cocomo_params.get('personnel_capability', 1.0),
            cocomo_params.get('personnel_experience', 1.0),
            cocomo_params.get('tool_experience', 1.0),
            cocomo_params.get('language_experience', 1.0),
            cocomo_params.get('team_cohesion', 1.0),
            cocomo_params.get('process_maturity', 1.0),
            cocomo_params.get('security_factor', 1.0)
        ]
        
        for em in effort_multipliers:
            em_product *= em
        
        # COCOMO II formula: PM = A * Size^(B + 0.01 * SF) * EM
        A = 2.94  # Coefficient
        B = 0.91  # Exponent
        
        effort = A * (size ** (B + 0.01 * sf_sum)) * em_product
        
        return effort
    
    def _calculate_fp_effort(self, fp_params):
        """
        Calculate effort using Function Points Analysis
        
        Args:
            fp_params (dict): Function Points parameters
            
        Returns:
            float: Effort in person-months
        """
        # Extract parameters
        external_inputs = fp_params.get('external_inputs', 0)
        external_outputs = fp_params.get('external_outputs', 0)
        external_inquiries = fp_params.get('external_inquiries', 0)
        internal_files = fp_params.get('internal_files', 0)
        external_files = fp_params.get('external_files', 0)
        complexity_multiplier = fp_params.get('complexity_multiplier', 1.0)
        
        # Weights for each component based on complexity
        # Using average complexity weights for simplicity
        weights = {
            'external_inputs': 4,      # Average weight
            'external_outputs': 5,     # Average weight
            'external_inquiries': 4,   # Average weight
            'internal_files': 10,      # Average weight
            'external_files': 7        # Average weight
        }
        
        # Calculate Function Points
        fp = (
            weights['external_inputs'] * external_inputs +
            weights['external_outputs'] * external_outputs +
            weights['external_inquiries'] * external_inquiries +
            weights['internal_files'] * internal_files +
            weights['external_files'] * external_files
        )
        
        # Apply complexity adjustment
        adjusted_fp = fp * complexity_multiplier
        
        # Convert FP to effort (person-months)
        # Industry average: 1 FP = 0.5 person-months
        effort = adjusted_fp * 0.5
        
        return effort
    
    def _calculate_ucp_effort(self, ucp_params):
        """
        Calculate effort using Use Case Points
        
        Args:
            ucp_params (dict): Use Case Points parameters
            
        Returns:
            float: Effort in person-months
        """
        # Extract parameters
        simple_actors = ucp_params.get('simple_actors', 0)
        average_actors = ucp_params.get('average_actors', 0)
        complex_actors = ucp_params.get('complex_actors', 0)
        
        simple_use_cases = ucp_params.get('simple_use_cases', 0)
        average_use_cases = ucp_params.get('average_use_cases', 0)
        complex_use_cases = ucp_params.get('complex_use_cases', 0)
        
        technical_factors = ucp_params.get('technical_factors', 1.0)
        environmental_factors = ucp_params.get('environmental_factors', 1.0)
        
        # Calculate Unadjusted Actor Weight (UAW)
        uaw = (simple_actors * 1) + (average_actors * 2) + (complex_actors * 3)
        
        # Calculate Unadjusted Use Case Weight (UUCW)
        uucw = (simple_use_cases * 5) + (average_use_cases * 10) + (complex_use_cases * 15)
        
        # Calculate Unadjusted Use Case Points (UUCP)
        uucp = uaw + uucw
        
        # Apply technical and environmental factors
        ucp = uucp * technical_factors * environmental_factors
        
        # Convert UCP to effort (person-hours)
        # Industry standard: 20 person-hours per UCP
        effort_hours = ucp * 20
        
        # Convert to person-months (assuming 160 hours per month)
        effort_months = effort_hours / 160
        
        return effort_months
    
    def suggest_team_composition(self, requirements_text):
        """
        Suggest team composition based on requirements analysis
        
        Args:
            requirements_text (str): Requirements document text
            
        Returns:
            dict: Suggested team composition
        """
        logger.info("Suggesting team composition")
        
        try:
            # Analyze requirements
            analysis = self.analyzer.analyze_requirements_document(requirements_text)
            
            # Get effort estimation
            effort = self.estimate_effort(requirements_text)['effort']
            
            # Extract key information
            technologies = analysis['summary'].get('technologies_detected', [])
            requirement_types = analysis['summary']['by_type']
            
            # Base roles
            roles = {
                'project_manager': 1,
                'software_developers': max(2, int(effort / 3)),  # 1 developer per 3 person-months
                'qa_engineers': max(1, int(effort / 6))          # 1 QA per 6 person-months
            }
            
            # Add specialized roles based on requirements
            if requirement_types.get('security', 0) > 0:
                roles['security_engineer'] = 1
                
            if requirement_types.get('data', 0) > 0:
                roles['database_engineer'] = 1
                
            if requirement_types.get('interface', 0) > 0 or requirement_types.get('usability', 0) > 0:
                roles['ui_ux_designer'] = 1
            
            # Add technology-specific roles
            tech_roles = {}
            
            frontend_techs = ['react', 'angular', 'vue', 'javascript', 'typescript', 'html', 'css']
            backend_techs = ['java', 'python', 'c#', 'node.js', 'php', 'go', 'ruby']
            db_techs = ['sql', 'mysql', 'postgresql', 'mongodb', 'oracle', 'cassandra']
            devops_techs = ['docker', 'kubernetes', 'jenkins', 'aws', 'azure', 'gcp', 'ci/cd']
            
            if any(tech in technologies for tech in frontend_techs):
                tech_roles['frontend_developers'] = max(1, int(roles['software_developers'] / 3))
                
            if any(tech in technologies for tech in backend_techs):
                tech_roles['backend_developers'] = max(1, int(roles['software_developers'] / 3))
                
            if any(tech in technologies for tech in db_techs):
                tech_roles['database_developers'] = 1
                
            if any(tech in technologies for tech in devops_techs):
                tech_roles['devops_engineers'] = 1
            
            # Calculate total team size
            total_team_size = sum(roles.values()) + sum(tech_roles.values())
            
            # Adjust software_developers to account for specialized developers
            roles['software_developers'] = max(1, roles['software_developers'] - sum(tech_roles.values()))
            
            result = {
                'team_size': total_team_size,
                'core_roles': roles,
                'technical_specialists': tech_roles,
                'estimated_effort': {
                    'total_effort': effort,
                    'unit': 'person_months'
                }
            }
            
            logger.info(f"Team composition suggestion completed: {total_team_size} team members")
            return result
            
        except Exception as e:
            logger.error(f"Error in team composition suggestion: {e}")
            raise
    
    def generate_effort_breakdown(self, requirements_text):
        """
        Generate a breakdown of effort by phase and component
        
        Args:
            requirements_text (str): Requirements document text
            
        Returns:
            dict: Effort breakdown
        """
        logger.info("Generating effort breakdown")
        
        try:
            # Analyze requirements
            analysis = self.analyzer.analyze_requirements_document(requirements_text)
            
            # Get total effort estimation
            total_effort = self.estimate_effort(requirements_text)['effort']
            
            # Typical phase distribution
            phase_distribution = {
                'requirements_analysis': 0.1,    # 10%
                'design': 0.15,                  # 15%
                'implementation': 0.4,           # 40%
                'testing': 0.2,                  # 20%
                'deployment': 0.05,              # 5%
                'project_management': 0.1        # 10%
            }
            
            # Adjust based on requirements complexity
            avg_complexity = analysis['summary']['avg_complexity']
            if avg_complexity > 2.0:
                # For complex projects, increase design and testing
                phase_distribution['design'] += 0.05
                phase_distribution['testing'] += 0.05
                phase_distribution['implementation'] -= 0.1
            elif avg_complexity < 1.5:
                # For simple projects, increase implementation
                phase_distribution['design'] -= 0.05
                phase_distribution['implementation'] += 0.1
                phase_distribution['testing'] -= 0.05
            
            # Calculate effort for each phase
            phase_effort = {}
            for phase, percentage in phase_distribution.items():
                phase_effort[phase] = round(total_effort * percentage, 2)
            
            # Component breakdown based on requirement types
            requirement_types = analysis['summary']['by_type']
            total_requirements = analysis['summary']['total_requirements']
            
            component_distribution = {}
            for req_type, count in requirement_types.items():
                if total_requirements > 0:
                    component_distribution[req_type] = round(count / total_requirements, 2)
            
            # Calculate effort for each component
            component_effort = {}
            implementation_effort = phase_effort['implementation']
            
            for component, percentage in component_distribution.items():
                component_effort[component] = round(implementation_effort * percentage, 2)
            
            result = {
                'total_effort': total_effort,
                'unit': 'person_months',
                'phase_breakdown': phase_effort,
                'component_breakdown': component_effort
            }
            
            logger.info("Effort breakdown generation completed")
            return result
            
        except Exception as e:
            logger.error(f"Error in effort breakdown generation: {e}")
            raise
    
    def generate_estimation_report(self, requirements_text, project_name="Software Project"):
        """
        Generate a comprehensive estimation report
        
        Args:
            requirements_text (str): Requirements document text
            project_name (str): Name of the project
            
        Returns:
            dict: Comprehensive estimation report
        """
        logger.info(f"Generating estimation report for project: {project_name}")
        
        try:
            # Get basic estimation
            estimation = self.estimate_effort(requirements_text)
            
            # Get team composition
            team = self.suggest_team_composition(requirements_text)
            
            # Get effort breakdown
            breakdown = self.generate_effort_breakdown(requirements_text)
            
            # Get requirements analysis
            analysis = self.analyzer.analyze_requirements_document(requirements_text)
            
            # Extract requirements by type for the report
            requirements_by_type = {}
            for req in analysis['requirements']:
                req_type = req['type']
                if req_type not in requirements_by_type:
                    requirements_by_type[req_type] = []
                
                requirements_by_type[req_type].append({
                    'id': req['id'],
                    'text': req['text'],
                    'complexity': req['complexity']
                })
            
            # Calculate project schedule
            total_effort = estimation['effort']  # in person-months
            team_size = team['team_size']
            
            # Simple schedule calculation
            if team_size > 0:
                calendar_months = round(total_effort / team_size * 1.2, 1)  # Add 20% buffer
            else:
                calendar_months = total_effort
            
            # Generate comprehensive report
            report = {
                'project_info': {
                    'name': project_name,
                    'estimated_effort': total_effort,
                    'effort_unit': estimation['unit'],
                    'estimated_duration': calendar_months,
                    'duration_unit': 'calendar_months',
                    'team_size': team['team_size']
                },
                'effort_estimation': {
                    'method_used': estimation['method_used'],
                    'total_effort': total_effort,
                    'all_predictions': estimation['all_predictions'],
                    'effort_breakdown': breakdown
                },
                'team_composition': {
                    'core_roles': team['core_roles'],
                    'technical_specialists': team['technical_specialists']
                },
                'requirements_analysis': {
                    'summary': analysis['summary'],
                    'requirements_by_type': requirements_by_type
                },
                'schedule': {
                    'calendar_months': calendar_months,
                    'suggested_phases': {
                        'requirements': {
                            'duration': round(calendar_months * 0.2, 1),
                            'effort': breakdown['phase_breakdown']['requirements_analysis']
                        },
                        'design': {
                            'duration': round(calendar_months * 0.25, 1),
                            'effort': breakdown['phase_breakdown']['design']
                        },
                        'implementation': {
                            'duration': round(calendar_months * 0.4, 1),
                            'effort': breakdown['phase_breakdown']['implementation']
                        },
                        'testing': {
                            'duration': round(calendar_months * 0.3, 1),
                            'effort': breakdown['phase_breakdown']['testing']
                        },
                        'deployment': {
                            'duration': round(calendar_months * 0.1, 1),
                            'effort': breakdown['phase_breakdown']['deployment']
                        }
                    }
                }
            }
            
            logger.info(f"Estimation report generated for project: {project_name}")
            return report
            
        except Exception as e:
            logger.error(f"Error in estimation report generation: {e}")
            raise

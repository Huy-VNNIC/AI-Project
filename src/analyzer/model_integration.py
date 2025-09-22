"""
Model integration module for software effort estimation
"""

import os
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.svm import SVR
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import xgboost as xgb
import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

class ModelSelector:
    """
    Model selector for software effort estimation based on project characteristics
    """
    
    def __init__(self, models_dir='models'):
        """
        Initialize the model selector
        
        Args:
            models_dir (str): Directory containing trained models
        """
        self.models_dir = models_dir
        self.models = {}
        self.meta_model = None
        self.load_models()
    
    def load_models(self):
        """
        Load pre-trained models from the models directory
        """
        if not os.path.exists(self.models_dir):
            print(f"Models directory {self.models_dir} does not exist. No models loaded.")
            return
        
        # Load standard models
        model_files = {
            'random_forest': 'rf_model.pkl',
            'xgboost': 'xgb_model.pkl',
            'linear_regression': 'linear_model.pkl',
            'svr': 'svr_model.pkl',
            'neural_network': 'nn_model.h5',
            'meta_model': 'meta_model.pkl'
        }
        
        for model_name, filename in model_files.items():
            model_path = os.path.join(self.models_dir, filename)
            if os.path.exists(model_path):
                try:
                    if model_name == 'neural_network':
                        self.models[model_name] = load_model(model_path)
                    else:
                        self.models[model_name] = joblib.load(model_path)
                    print(f"Loaded model: {model_name}")
                except Exception as e:
                    print(f"Error loading {model_name}: {e}")
        
        # Load meta-model if available
        meta_model_path = os.path.join(self.models_dir, 'meta_model.pkl')
        if os.path.exists(meta_model_path):
            try:
                self.meta_model = joblib.load(meta_model_path)
                print("Loaded meta-model for model selection")
            except Exception as e:
                print(f"Error loading meta-model: {e}")
    
    def select_best_model(self, features):
        """
        Select the best model based on project features
        
        Args:
            features (dict): Project features
            
        Returns:
            str: Name of the best model
        """
        if not self.meta_model or not self.models:
            # Default to random forest if meta-model not available
            return 'random_forest' if 'random_forest' in self.models else list(self.models.keys())[0]
        
        # Prepare features for meta-model
        # (Convert features dict to the format expected by the meta-model)
        feature_vector = self._prepare_features_for_meta_model(features)
        
        # Get model recommendation from meta-model
        best_model = self.meta_model.predict(feature_vector)[0]
        
        # Ensure the recommended model is available
        if best_model in self.models:
            return best_model
        else:
            # Fall back to first available model
            return list(self.models.keys())[0]
    
    def _prepare_features_for_meta_model(self, features):
        """
        Convert feature dictionary to format expected by meta-model
        
        Args:
            features (dict): Project features
            
        Returns:
            numpy.ndarray: Feature vector for meta-model
        """
        # This needs to be customized based on your meta-model's expected input format
        # As a simple example, we'll extract a few key features
        
        # Define the expected features in the correct order
        expected_features = [
            'num_requirements', 'avg_complexity', 'size_kloc', 
            'external_inputs', 'external_outputs', 'external_inquiries',
            'internal_files', 'external_files', 'technical_factors',
            'environmental_factors'
        ]
        
        # Create feature vector
        feature_vector = []
        for feature in expected_features:
            # Use 0 as default if feature not available
            feature_vector.append(features.get(feature, 0))
        
        return np.array([feature_vector])
    
    def predict(self, features, model_name=None):
        """
        Make effort prediction using the specified or best model
        
        Args:
            features (dict): Project features
            model_name (str, optional): Model to use for prediction
            
        Returns:
            float: Predicted effort (person-months)
        """
        if not self.models:
            raise ValueError("No models available for prediction")
        
        # Select model to use
        if not model_name:
            model_name = self.select_best_model(features)
        
        if model_name not in self.models:
            available_models = list(self.models.keys())
            if not available_models:
                raise ValueError("No models available for prediction")
            model_name = available_models[0]
        
        # Prepare features for the selected model
        feature_vector = self._prepare_features_for_model(features, model_name)
        
        # Make prediction
        model = self.models[model_name]
        
        if model_name == 'neural_network':
            # Neural network models need different handling
            return float(model.predict(feature_vector)[0][0])
        else:
            return float(model.predict(feature_vector)[0])
    
    def _prepare_features_for_model(self, features, model_name):
        """
        Prepare features for the specified model
        
        Args:
            features (dict): Project features
            model_name (str): Model name
            
        Returns:
            numpy.ndarray: Feature vector for the model
        """
        # Define common features for all models
        common_features = [
            'num_requirements', 'avg_complexity', 'size_kloc', 
            'external_inputs', 'external_outputs', 'external_inquiries',
            'internal_files', 'external_files', 'technical_factors',
            'environmental_factors', 'num_entities', 'num_technologies'
        ]
        
        # Add model-specific features
        if model_name == 'neural_network':
            # Neural networks might use additional features
            additional_features = ['num_verbs', 'num_nouns', 'num_adjectives', 'avg_sentence_length']
            all_features = common_features + additional_features
        else:
            all_features = common_features
        
        # Create feature vector
        feature_vector = []
        for feature in all_features:
            # Use 0 as default if feature not available
            feature_vector.append(features.get(feature, 0))
        
        return np.array([feature_vector])
    
    def predict_all_models(self, features):
        """
        Make predictions using all available models
        
        Args:
            features (dict): Project features
            
        Returns:
            dict: Predictions from all models
        """
        predictions = {}
        for model_name in self.models:
            try:
                predictions[model_name] = self.predict(features, model_name)
            except Exception as e:
                print(f"Error predicting with {model_name}: {e}")
                predictions[model_name] = None
        
        return predictions
    
    def get_ensemble_prediction(self, features):
        """
        Get ensemble prediction by averaging all model predictions
        
        Args:
            features (dict): Project features
            
        Returns:
            float: Ensemble prediction
        """
        predictions = self.predict_all_models(features)
        valid_predictions = [pred for pred in predictions.values() if pred is not None]
        
        if not valid_predictions:
            raise ValueError("No valid predictions available")
        
        return sum(valid_predictions) / len(valid_predictions)


class ModelTrainer:
    """
    Trainer for software effort estimation models
    """
    
    def __init__(self, save_dir='models'):
        """
        Initialize the model trainer
        
        Args:
            save_dir (str): Directory to save trained models
        """
        self.save_dir = save_dir
        
        # Create save directory if it doesn't exist
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
    
    def prepare_data(self, data_path):
        """
        Prepare data for model training
        
        Args:
            data_path (str): Path to dataset
            
        Returns:
            tuple: X, y for training
        """
        # Load data
        if data_path.endswith('.csv'):
            df = pd.read_csv(data_path)
        elif data_path.endswith('.xlsx'):
            df = pd.read_excel(data_path)
        else:
            raise ValueError(f"Unsupported file format: {data_path}")
        
        # Identify target column (effort)
        target_candidates = ['effort', 'Effort', 'actual_effort', 'effort_months', 'person_months']
        target_col = None
        
        for candidate in target_candidates:
            if candidate in df.columns:
                target_col = candidate
                break
        
        if target_col is None:
            raise ValueError("Could not identify effort column in dataset")
        
        # Split features and target
        y = df[target_col].values
        X = df.drop(target_col, axis=1)
        
        # Remove any non-numeric columns
        X = X.select_dtypes(include=['int64', 'float64'])
        
        return X, y
    
    def train_random_forest(self, X, y):
        """
        Train Random Forest regression model
        
        Args:
            X (DataFrame): Features
            y (ndarray): Target values
            
        Returns:
            RandomForestRegressor: Trained model
        """
        # Create pipeline with scaling
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('rf', RandomForestRegressor(n_estimators=100, random_state=42))
        ])
        
        # Parameter grid for hyperparameter tuning
        param_grid = {
            'rf__n_estimators': [50, 100, 200],
            'rf__max_depth': [None, 10, 20, 30],
            'rf__min_samples_split': [2, 5, 10]
        }
        
        # Grid search with cross-validation
        grid_search = GridSearchCV(
            pipeline, param_grid, cv=5, scoring='neg_mean_squared_error'
        )
        
        grid_search.fit(X, y)
        
        # Get best model
        best_model = grid_search.best_estimator_
        
        # Save model
        joblib.dump(best_model, os.path.join(self.save_dir, 'rf_model.pkl'))
        
        return best_model
    
    def train_xgboost(self, X, y):
        """
        Train XGBoost regression model
        
        Args:
            X (DataFrame): Features
            y (ndarray): Target values
            
        Returns:
            XGBRegressor: Trained model
        """
        # Create pipeline with scaling
        pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('xgb', xgb.XGBRegressor(objective='reg:squarederror', random_state=42))
        ])
        
        # Parameter grid for hyperparameter tuning
        param_grid = {
            'xgb__n_estimators': [50, 100, 200],
            'xgb__max_depth': [3, 5, 7],
            'xgb__learning_rate': [0.01, 0.05, 0.1]
        }
        
        # Grid search with cross-validation
        grid_search = GridSearchCV(
            pipeline, param_grid, cv=5, scoring='neg_mean_squared_error'
        )
        
        grid_search.fit(X, y)
        
        # Get best model
        best_model = grid_search.best_estimator_
        
        # Save model
        joblib.dump(best_model, os.path.join(self.save_dir, 'xgb_model.pkl'))
        
        return best_model
    
    def train_neural_network(self, X, y):
        """
        Train neural network regression model
        
        Args:
            X (DataFrame): Features
            y (ndarray): Target values
            
        Returns:
            Sequential: Trained model
        """
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Save scaler for future use
        joblib.dump(scaler, os.path.join(self.save_dir, 'nn_scaler.pkl'))
        
        # Build model
        input_dim = X.shape[1]
        
        model = Sequential([
            Dense(64, activation='relu', input_dim=input_dim),
            Dropout(0.2),
            Dense(32, activation='relu'),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1)  # Output layer
        ])
        
        # Compile model
        model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        
        # Early stopping
        early_stopping = EarlyStopping(
            monitor='val_loss', patience=10, restore_best_weights=True
        )
        
        # Train model
        model.fit(
            X_scaled, y,
            epochs=100,
            batch_size=32,
            validation_split=0.2,
            callbacks=[early_stopping],
            verbose=1
        )
        
        # Save model
        model.save(os.path.join(self.save_dir, 'nn_model.h5'))
        
        return model
    
    def train_all_models(self, data_path):
        """
        Train all supported models
        
        Args:
            data_path (str): Path to dataset
            
        Returns:
            dict: Trained models
        """
        # Prepare data
        X, y = self.prepare_data(data_path)
        
        # Train models
        models = {}
        
        # Random Forest
        print("Training Random Forest model...")
        rf_model = self.train_random_forest(X, y)
        models['random_forest'] = rf_model
        
        # XGBoost
        print("Training XGBoost model...")
        xgb_model = self.train_xgboost(X, y)
        models['xgboost'] = xgb_model
        
        # Linear Regression
        print("Training Linear Regression model...")
        lr_pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('lr', LinearRegression())
        ])
        lr_pipeline.fit(X, y)
        joblib.dump(lr_pipeline, os.path.join(self.save_dir, 'linear_model.pkl'))
        models['linear_regression'] = lr_pipeline
        
        # SVR
        print("Training SVR model...")
        svr_pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('svr', SVR())
        ])
        svr_pipeline.fit(X, y)
        joblib.dump(svr_pipeline, os.path.join(self.save_dir, 'svr_model.pkl'))
        models['svr'] = svr_pipeline
        
        # Neural Network
        print("Training Neural Network model...")
        nn_model = self.train_neural_network(X, y)
        models['neural_network'] = nn_model
        
        # Train meta-model
        print("Training meta-model for model selection...")
        self.train_meta_model(X, y, models)
        
        return models
    
    def train_meta_model(self, X, y, models):
        """
        Train a meta-model to select the best model for each project
        
        Args:
            X (DataFrame): Features
            y (ndarray): Target values
            models (dict): Trained models
            
        Returns:
            object: Trained meta-model
        """
        # Create meta-features based on project characteristics
        meta_X = X.copy()
        
        # Add performance metrics for each model as features
        for model_name, model in models.items():
            if model_name != 'neural_network':
                y_pred = model.predict(X)
                meta_X[f'{model_name}_error'] = np.abs(y - y_pred)
            else:
                # Handle neural network differently
                scaler = joblib.load(os.path.join(self.save_dir, 'nn_scaler.pkl'))
                X_scaled = scaler.transform(X)
                y_pred = model.predict(X_scaled).flatten()
                meta_X[f'{model_name}_error'] = np.abs(y - y_pred)
        
        # Create target labels for meta-model (which model performs best)
        best_model_idx = np.argmin([
            meta_X[f'{model_name}_error'].values for model_name in models
        ], axis=0)
        
        model_names = list(models.keys())
        best_model_names = [model_names[idx] for idx in best_model_idx]
        
        # Convert to categorical labels
        model_to_idx = {name: i for i, name in enumerate(model_names)}
        meta_y = np.array([model_to_idx[name] for name in best_model_names])
        
        # Drop error columns for training
        for model_name in models:
            meta_X = meta_X.drop(f'{model_name}_error', axis=1)
        
        # Train a Random Forest classifier as meta-model
        meta_model = RandomForestClassifier(n_estimators=100, random_state=42)
        meta_model.fit(meta_X, meta_y)
        
        # Save meta-model
        joblib.dump(meta_model, os.path.join(self.save_dir, 'meta_model.pkl'))
        
        # Also save model mapping
        joblib.dump(model_to_idx, os.path.join(self.save_dir, 'model_mapping.pkl'))
        
        return meta_model
    
    def evaluate_models(self, data_path, test_size=0.2):
        """
        Evaluate all models on a dataset
        
        Args:
            data_path (str): Path to dataset
            test_size (float): Proportion of data to use for testing
            
        Returns:
            dict: Evaluation metrics for each model
        """
        # Prepare data
        X, y = self.prepare_data(data_path)
        
        # Split into training and testing sets
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42
        )
        
        # Train models
        models = {}
        
        # Random Forest
        rf_pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('rf', RandomForestRegressor(n_estimators=100, random_state=42))
        ])
        rf_pipeline.fit(X_train, y_train)
        models['random_forest'] = rf_pipeline
        
        # XGBoost
        xgb_pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('xgb', xgb.XGBRegressor(objective='reg:squarederror', random_state=42))
        ])
        xgb_pipeline.fit(X_train, y_train)
        models['xgboost'] = xgb_pipeline
        
        # Linear Regression
        lr_pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('lr', LinearRegression())
        ])
        lr_pipeline.fit(X_train, y_train)
        models['linear_regression'] = lr_pipeline
        
        # SVR
        svr_pipeline = Pipeline([
            ('scaler', StandardScaler()),
            ('svr', SVR())
        ])
        svr_pipeline.fit(X_train, y_train)
        models['svr'] = svr_pipeline
        
        # Neural Network
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        input_dim = X_train.shape[1]
        nn_model = Sequential([
            Dense(64, activation='relu', input_dim=input_dim),
            Dropout(0.2),
            Dense(32, activation='relu'),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1)
        ])
        nn_model.compile(optimizer='adam', loss='mse', metrics=['mae'])
        
        early_stopping = EarlyStopping(
            monitor='val_loss', patience=10, restore_best_weights=True
        )
        
        nn_model.fit(
            X_train_scaled, y_train,
            epochs=100,
            batch_size=32,
            validation_split=0.2,
            callbacks=[early_stopping],
            verbose=0
        )
        
        # Evaluate models
        metrics = {}
        
        for model_name, model in models.items():
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            mse = mean_squared_error(y_test, y_pred)
            rmse = np.sqrt(mse)
            mae = mean_absolute_error(y_test, y_pred)
            r2 = r2_score(y_test, y_pred)
            
            metrics[model_name] = {
                'MSE': mse,
                'RMSE': rmse,
                'MAE': mae,
                'R2': r2
            }
        
        # Neural Network metrics
        y_pred_nn = nn_model.predict(X_test_scaled).flatten()
        
        mse = mean_squared_error(y_test, y_pred_nn)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred_nn)
        r2 = r2_score(y_test, y_pred_nn)
        
        metrics['neural_network'] = {
            'MSE': mse,
            'RMSE': rmse,
            'MAE': mae,
            'R2': r2
        }
        
        # Ensemble prediction (average of all models)
        y_pred_ensemble = np.zeros_like(y_test)
        
        for model_name, model in models.items():
            y_pred_ensemble += model.predict(X_test)
        
        y_pred_ensemble += nn_model.predict(X_test_scaled).flatten()
        y_pred_ensemble /= (len(models) + 1)
        
        # Calculate ensemble metrics
        mse = mean_squared_error(y_test, y_pred_ensemble)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred_ensemble)
        r2 = r2_score(y_test, y_pred_ensemble)
        
        metrics['ensemble'] = {
            'MSE': mse,
            'RMSE': rmse,
            'MAE': mae,
            'R2': r2
        }
        
        return metrics

# Import necessary libraries
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.impute import SimpleImputer
import joblib

# Load data
data = pd.read_csv('synthetic_fraud_data.csv')

# Step 1: Basic Data Preprocessing

# Check for missing values
data.isnull().sum()

# Step 2: Feature Engineering

# 2.1 Extract features from timestamp
data['timestamp'] = pd.to_datetime(data['timestamp'])
data['day_of_week'] = data['timestamp'].dt.dayofweek  # Monday=0, Sunday=6
data['is_weekend'] = data['day_of_week'].isin([5, 6]).astype(int)
data['transaction_hour'] = data['timestamp'].dt.hour

# 2.2 Parse 'velocity_last_hour' to extract useful features
# Assume 'velocity_last_hour' is in JSON-like format; here we parse and create new features
data['velocity_last_hour'] = data['velocity_last_hour'].apply(eval)  # Convert string to dictionary
data['num_transactions_last_hour'] = data['velocity_last_hour'].apply(lambda x: x['num_transactions'])
data['total_amount_last_hour'] = data['velocity_last_hour'].apply(lambda x: x['total_amount'])

# Drop unnecessary columns
data = data.drop(columns=['transaction_id', 'customer_id', 'timestamp', 'velocity_last_hour', 'device_fingerprint'])

# Step 3: Data Preprocessing Pipeline

# Identify categorical and numerical columns
categorical_features = ['merchant_category', 'merchant_type', 'merchant', 'currency', 'country', 
                        'city', 'city_size', 'card_type', 'device', 'channel']
numerical_features = ['amount', 'distance_from_home', 'transaction_hour', 'num_transactions_last_hour', 'total_amount_last_hour']

# Define preprocessing for numerical data: scaling
numeric_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='median')),
    ('scaler', StandardScaler())])

# Define preprocessing for categorical data: one-hot encoding
categorical_transformer = Pipeline(steps=[
    ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
    ('onehot', OneHotEncoder(handle_unknown='ignore'))])

# Combine preprocessors in a column transformer
preprocessor = ColumnTransformer(
    transformers=[
        ('num', numeric_transformer, numerical_features),
        ('cat', categorical_transformer, categorical_features)])

# Step 4: Define the Model Pipeline

# Random Forest model pipeline with preprocessing
model_pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('classifier', RandomForestClassifier(random_state=42))])

# Step 5: Split Data

X = data.drop(columns=['is_fraud'])
y = data['is_fraud']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)

# Step 6: Hyperparameter Tuning with Grid Search

param_grid = {
    'classifier__n_estimators': [100, 200],
    'classifier__max_depth': [10, 20, None],
    'classifier__min_samples_split': [2, 5, 10]
}

grid_search = GridSearchCV(model_pipeline, param_grid, cv=3, scoring='f1', n_jobs=-1)
grid_search.fit(X_train, y_train)

# Retrieve the best model
best_model = grid_search.best_estimator_

# Step 7: Model Evaluation

# Predictions and evaluation on test data
y_pred = best_model.predict(X_test)
print("Classification Report:\n", classification_report(y_test, y_pred))
roc_auc = roc_auc_score(y_test, y_pred)
print(f"ROC-AUC Score: {roc_auc}")

# Step 8: Save the model
joblib.dump(best_model, 'fraud_detection_model.pkl')

# Import necessary libraries
import joblib
import pandas as pd

# Load the saved model
model = joblib.load('fraud_detection_model.pkl')

# Sample input data for prediction
new_data = pd.DataFrame({
    'amount': [500.0],
    'distance_from_home': [1],
    'transaction_hour': [13],
    'merchant_category': ['Retail'],
    'merchant_type': ['online'],
    'merchant': ['Amazon'],
    'currency': ['USD'],
    'country': ['United States'],
    'city': ['New York'],
    'city_size': ['large'],
    'card_type': ['debit'],
    'device': ['Chrome'],
    'channel': ['web'],
    'day_of_week': [2],
    'is_weekend': [0],
    'num_transactions_last_hour': [3],
    'total_amount_last_hour': [1500.0],
})

# Make prediction using the model
prediction = model.predict(new_data)

# Interpreting prediction result
if prediction[0] == 1:
    print("Prediction: Fraudulent Transaction")
else:
    print("Prediction: Non-Fraudulent Transaction")
    
# Get probability of each class (non-fraud and fraud)
proba = model.predict_proba(new_data)

print(f"Probability of Non-Fraudulent Transaction: {proba[0][0]:.2f}")
print(f"Probability of Fraudulent Transaction: {proba[0][1]:.2f}")

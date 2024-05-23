import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib
import matplotlib.pyplot as plt

# Function to read and process transaction data
def read_process_transactions(file_name):
    transactions = pd.read_csv(file_name + '.csv')
    transactions['postDate'] = pd.to_datetime(transactions['Date'])
    transactions.sort_values(by='postDate', inplace=True)
    transactions['total_balance'] = transactions['balance'].cumsum()
    return transactions[['postDate', 'total_balance']]

# Function to create features for the Random Forest model
def create_features(data):
    data['week'] = data['postDate'].dt.dayofweek
    data['quarter'] = data['postDate'].dt.quarter
    data['month'] = data['postDate'].dt.month
    data['year'] = data['postDate'].dt.year
    data['dayofyear'] = data['postDate'].dt.dayofyear
    data['dayofmonth'] = data['postDate'].dt.day
    data['dayofweek'] = data['postDate'].dt.dayofweek
    return data

# Read and process the data
data = read_process_transactions('../ai/generated_data/fake_bank_account_transactions2')
data = create_features(data)
data.set_index('postDate', inplace=True)

# Prepare the data for the model
FEATURES = ['week', 'quarter', 'month', 'year', 'dayofyear', 'dayofmonth', 'dayofweek']
TARGET = 'total_balance'
X = data[FEATURES]
y = data[TARGET]

# Split the data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and train the Random Forest model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save the model to a file
joblib.dump(model, 'random_forest_model.joblib')

y_pred = model.predict(X_test)

# Plotting the actual vs predicted values
plt.figure(figsize=(10, 5))
plt.plot(y_test.index, y_test, label='Actual')
plt.plot(y_test.index, y_pred, label='Predicted', linestyle='--')
plt.title('Test Data vs Predicted Data')
plt.xlabel('Date')
plt.ylabel('Total Balance')
plt.legend()
plt.show()

# Plotting function with the new color scheme
def plot_feature_importances(model, features):
    importances = model.feature_importances_
    indices = np.argsort(importances)
    plt.figure(figsize=(10, 6))
    plt.barh(range(len(indices)), importances[indices], color=['#343a40', '#0077bb', '#d9d9d9', '#fafafe', '#abb5be'])
    plt.yticks(range(len(indices)), [features[i] for i in indices])
    plt.xlabel('Feature Importance')
    plt.show()

# Plot the feature importances
plot_feature_importances(model, FEATURES)

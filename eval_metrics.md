## Code snippet

```python
params = {  "n_neighbors":10,
            "metric":"manhattan",
            "weights":"distance",
            "algorithm":"kd_tree"
         }
model = KNeighborsRegressor(**params)
```

## Metrics

|Metric | Training set | Test set | 
| ---------- | ---------- |-------|
|MAE | 258.692 | 53892.876 | 
|RMSE | 5825.555 | 110909.905 | 
|R2 | 1 | 0.814 | 
|MAPE | 0.061 | 13.173 | 
|sMAPE | 0.059 | 12.519 | 

## Features

|From Immoweb|Derived data|External data|
| ---------- | ---------- |-------|
| Property type | Age of the property (Construction year) | Latitude |
| Subtype | Region (Locality - zipcode) | Longitude |
| Bedrooms |  | Taxes |
| Living area |  | Population Density |
| Bathrooms |  | Income |
| Terrace Area |  |  |
| EPC score |  |  |
| Land surface |  |  |
| Facades |  |  |
| Building state |  |  |

## Accuracy computing procedure
Test set which is 20% of the data

## Efficiency
Time taken for the model training: 5.638 seconds.

## Dataset usage 

1. Data scraped from Immoweb : 17586 rows, 22 columns
   ```plaintext
   Scraping was repeated to include EPC score and number of bathrooms
   ```
   
2. Cleaning the data: Removing duplicates : 13431 rows

3. Data cleaning : 13117 rows
   ```plaintext
   Drop rows with zipcode not in Belgium (Found few Spanish properties)
   Outliers = Living area > 2000, Land surface > 20,000, Price > 2,000,000
   Cap the data limit : Bathrooms max 5, Bedrooms max 8, Terrace area max 100
   Derived columns : 
   Age = 2024 - Construction year
   Region = Brussels/Flanders/Wallonia (Based on zip code)
   ```
   
4. Enrich data with additional information from external sources
    ```plaintext
    Added latitude, longitude for every zipcode
    Addded income, population density and taxes collected for each zipcode
     ```

5. Encoding categorical columns :
    ```plaintext
    Property type ( 0 = House , 1 = Apartment)
    EPC score  (Scale of 0-5)
    Building state ( Scale 0-2)
    Property subtype (Scale 0-4)
    Region (Scale 1-3)
    ```

6. Selecting features based on correlation and model performance
    ```plaintext
    Drop columns like Type sale,Garden Area,Equipped kitchen,Construction year,Locality,Open Fire
    ```

7. Splitting the dataset
    ```plaintext
    80% training and 20% test
    ```

8. Scaling the split dataset
    ```plaintext
    Use the scaling of training set to transform the test set
    ```

9. Hyperparameter tuning using GridSearchCV
   ```python
   param_dist = {
      'n_neighbors': randint(1, 20, 2),
      'weights': ['uniform', 'distance'],
      'algorithm': ['auto', 'ball_tree', 'kd_tree', 'brute'],
       'metric': ['minkowski','euclidean','manhattan'],
   }
   ```


About the model [KNNRegression](https://docs.google.com/presentation/d/15Yt92dLl2aA6XxnksoBJX_6Kiz0GpdbVQN5I1_e4id8/edit?usp=sharing)

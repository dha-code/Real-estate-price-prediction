## Code snippet

```python
params = {  "n_neighbors":12,
            "metric":"manhattan",
            "weights":"distance",
            "algorithm":"kd_tree"
         }
model = KNeighborsRegressor(**params)
```

## Metrics

|Metric | Training set | Test set | 
| ---------- | ---------- |-------|
|MAE | 234.666 | 58160.078 | 
|RMSE | 5292.321 | 117746.188 | 
|R2 | 1 | 0.794 | 
|MAPE | 0.064 | 14.17 | 
|sMAPE | 0.062 | 13.409 | 

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
TO-DO

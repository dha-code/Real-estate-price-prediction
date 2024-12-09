import pandas as pd
from sklearn.utils import resample
from utils.RealEstateKNNReg import RealEstateKNN
from time import perf_counter
start_time = perf_counter()

def balance_dataset(dataset_majority, dataset_minority, upsample_count):
    """
    Function to balance teh dataset for the property type
    """
    upsampled_set = resample(dataset_minority, 
                        replace=True,     
                        n_samples=upsample_count,
                        random_state=123 
                        ) 
    combined_set = pd.concat([dataset_majority,upsampled_set], ignore_index=True)
    return combined_set

# Read the input file with the pre-processed property data
immo_knn = pd.read_csv('./data/KNNInput.txt')

# Balance the dataset based ont he property type
house_count = immo_knn[immo_knn["Property type"] == 1].shape[0]
immo_house = immo_knn[immo_knn["Property type"] == 1]
immo_apt = immo_knn[immo_knn["Property type"] == 0]
balanced_set = balance_dataset(immo_house, immo_apt, house_count)

# Create an object of the RealEstateKNN class based on the params defined
params = {"dataset":balanced_set, 
            "target":"Price",
            "n_neighbors":10,
            "metric":"manhattan",
            "weights":"distance",
            "algorithm":"kd_tree"}

knn_model = RealEstateKNN(**params) #dataset=balanced_set, target="Price", n_neighbors=14, metric='manhattan', weights='distance', algorithm='ball_tree', p=1)

# Call the class functions to perform the steps required to train and test the KNN regressor model
knn_model.set_feature_target()

# Train and evaluate the model 
start_model_time = perf_counter()
knn_model.train_model()
knn_model.evaluate()
print(f"\nTime taken to train and evaluate model: {round(perf_counter()-start_model_time,3)} seconds.") 

# Print the metrics and generate graphs
knn_model.print_metrics()
knn_model.generate_graphs()
print(f"\nTime taken to from start to finish: {round(perf_counter()-start_time,3)} seconds.") 
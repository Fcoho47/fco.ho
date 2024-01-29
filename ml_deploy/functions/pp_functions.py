import numpy as np
import pandas as pd
import csv
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt

from sklearn.model_selection import train_test_split
from sklearn.decomposition import PCA
from sklearn import preprocessing
from sklearn import datasets
from sklearn.manifold import TSNE, MDS
import umap

def reduce_dim_by(data, method, labels, perplexity = None, n_iter = None, max_iter = None, n_neighbors = None):

    '''
    This function reduces the dimensionality of the data using the method specified.
    The method can be PCA, TSNE, MDS or UMAP.

    PCA method does not require any parameters.
    TSNE method requires perplexity and n_iter parameters.
    MDS method requires max_iter parameter.
    UMAP method requires n_neighbors parameter.
    '''

    ############################
    #TO DO
    #what happen if the data doesnt have categorical variables?
    #return a dataframe with classes information

    #save the classes information
    label_list = data[labels]

    #drop categorical variables
    for column, values in data.dtypes.items():
        if values == 'object':
            data = data.drop(column, axis=1)

    if method == 'PCA':
        dim_red = PCA(n_components=2).fit(data)
        data_new_dimensions = dim_red.transform(data)
        new_data = [x + [y] for x,y in zip(data_new_dimensions.tolist(), label_list)]
        return pd.DataFrame(new_data, columns=["X", "Y", 'class'])

    elif method == 'TSNE':
        data_new_dimensions = TSNE(n_components=2, perplexity=perplexity,
                               n_iter=n_iter, init="random").fit_transform(data)
        new_data = [x + [y] for x,y in zip(data_new_dimensions.tolist(), label_list)]
        return pd.DataFrame(new_data, columns=["X", "Y", 'class'])

    elif method == 'MDS':
        data_new_dimensions = MDS(n_components=2, max_iter=max_iter,
        normalized_stress="auto").fit_transform(data)
        new_data = [x + [y] for x,y in zip(data_new_dimensions.tolist(), label_list)]
        return pd.DataFrame(new_data, columns=["X", "Y", 'class'])

    elif method == 'UMAP':
        data_new_dimensions = umap.UMAP(n_neighbors=n_neighbors).fit_transform(data)
        new_data = [x + [y] for x,y in zip(data_new_dimensions.tolist(), label_list)]
        return pd.DataFrame(new_data, columns=["X", "Y", 'class'])

    else:
        print('Invalid method')
        return None
    

def make_chart(reduced_dataset, method):
    '''
    This function makes a chart of the data using the method specified.
    '''

    ############################
    #TO DO
    #adjust the entry variables with the information returned by the reduce_dim_by function

    #drop the categorical data
    source = pd.DataFrame(reduced_dataset.copy())

    chart = alt.Chart(source).mark_circle().encode(
        x=alt.X('X', axis=alt.Axis(title=f'{method}-X')),
        y=alt.Y('Y', axis=alt.Axis(title=f'{method}-Y')),
        color=alt.Color('class:N'),
    ).properties(width=400, height=200, title = f'{method} reduction')
    
    return chart


def outlier_remover(data, threshold, percentile):
    '''
    This function removes the outliers from the dataframe.
    it takes the dataframe, the threshold and the percentile as parameters.

    
    '''

    final_data = data.copy()
    percentiles = [percentile, 100-percentile]

    #drop categorical variables
    for column, values in data.dtypes.items():
        if values == 'object':
            data = data.drop(column, axis=1)
  

    #calculate the percentile
    percentile_list = []
    for column in data.columns:
        percentile_value = np.percentile(data[column], percentiles)
        percentile_list.append(percentile_value)

    #identify and remove the outliers
    idx_list = []
    for idx, values in data.iterrows():
        c = 0
        for column in data.columns:
            if (
                values[column] > percentile_list[data.columns.get_loc(column)][1] or
                values[column] < percentile_list[data.columns.get_loc(column)][0]
            ):

                c += 1
        if c >= threshold:
            #remove the row
            final_data = final_data.drop(idx, axis=0)

            #identify what are the indexes of the outliers
            idx_list.append(idx)

    #reset the index
    final_data = final_data.reset_index(drop=True)

    return final_data, idx_list
import pandas as pd
import tempfile
import mlflow
from sklearn.preprocessing import StandardScaler
import os
from pathlib import Path


def get_features():
    return {
        "numeric_columns": [
            "Age", "Years_At_Company", "Performance_Score",
            "Work_Hours_Per_Week", "Projects_Handled",
            "Overtime_Hours", "Sick_Days", "Remote_Work_Frequency",
            "Team_Size", "Training_Hours", "Promotions"
        ],
        "one_hot_encode_columns": [
            "Department", "Gender", "Job_Title", "Education_Level"
        ],
        "target": [
            "Employee_Satisfaction_Score"
        ]
    }

def one_hot_encode(df, columns: list):
    """One Hot Encode a column and return to main data."""
    return pd.get_dummies(df, columns=columns,
                          drop_first=True)

def standardize(df, columns: list,
                pre_scaler: StandardScaler=None,
                return_scaler: bool=False):
    """Standardize columns of the dataset."""
    if pre_scaler is None:
        scaler = StandardScaler()
        standardized_data = scaler.fit_transform(df[columns])
    else:
        scaler = pre_scaler
        standardized_data = scaler.transform(df[columns])

    standardized_df = pd.DataFrame(standardized_data,
                                   columns=columns,
                                   index=df.index)

    if return_scaler:
        return standardized_df, scaler
    return standardized_df


def log_figure(fig, artifact_path):
    """
    Log a matplotlib figure as an artifact in MLflow.

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Provide the figure object to log.
    artifact_path : str, optional
        Specify the filename for the artifact (default is 'figure.png').

    Returns
    -------
    None
        Log the figure as an artifact in the active MLflow run.
    
    Notes
    -----
    URI setting is assumed to be done outside this function. Set the
    correct MLFlow URI prior to execution.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = f"{temp_dir}/{artifact_path}"
        fig.savefig(file_path, format="png", dpi=300)
<<<<<<< HEAD
        mlflow.log_artifact(file_path)




def load_raw_data():
    """
    Load the local copy of the raw data.
    """
    file_path = os.path.join(
        Path.cwd().parent,
        'dataset\\Extended_Employee_Performance_and_Productivity_Data.csv'
    )
    print("Found" if os.path.exists(file_path) else "Not Found")
    # Check if the file exists before loading
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    data_df = pd.read_csv(file_path)
    return data_df

def transformed_employee_performance(data_df: pd.DataFrame) -> pd.DataFrame:
    """
    Transform data in preparation for feature engineering.
    """
    data_df['Hire_Date'] = pd.to_datetime(data_df['Hire_Date'])
    data_df['Hire_Date_int'] = (data_df['Hire_Date']
                                    .astype('int64') // 10**9)
    data_df.drop('Hire_Date', axis=1, inplace=True)
    return data_df

def feature_training(
        data_df: pd.DataFrame,
        X_scaler: StandardScaler = None,
        y_scaler: StandardScaler = None,
        reset_index: bool = False,
        return_scaler: bool = False
    ) -> tuple[pd.DataFrame, StandardScaler,
               StandardScaler]:
    """
    Feature engineer the HR Performance dataset.

    Parameters
    ----------
    data_df : pd.DataFrame
        The input dataset containing employee performance data.
    scaler : StandardScaler, optional
        A pre-fitted scaler. If None, a new scaler is trained.
    reset_index : bool, optional
        Whether to reset the index of the returned DataFrame.
    return_scaler : bool, optional
        If True, returns both the transformed DataFrame and the scaler.

    Returns
    -------
    pd.DataFrame or tuple(pd.DataFrame, StandardScaler, StandardScaler)
        The transformed dataset (and the fitted scaler if `return_scaler=True`).
    """
    numeric_columns = get_features()['numeric_columns']
    target_column = get_features()['target']

    def scale_data(columns: list,
                   sub_scaler: StandardScaler=None):
        if sub_scaler is None:
            sub_scaler = StandardScaler()
            std_values = sub_scaler.fit_transform(data_df[columns])
        else:
            std_values = sub_scaler.transform(data_df[columns])
        return (std_values, sub_scaler)

    X_std_values, X_scaler = scale_data(numeric_columns, X_scaler)
    y_std_values, y_scaler = scale_data(target_column, y_scaler)

    std_df = pd.DataFrame(X_std_values,
                          columns=numeric_columns)
    std_df[target_column[0]] = y_std_values

    new_df = one_hot_encode(
        data_df,
        get_features()['one_hot_encode_columns']
    )

    if reset_index:
        new_df.reset_index(inplace=True,
                           drop=True)

    categorical_columns = new_df.select_dtypes(
        include=['int', 'int64']
    ).columns
    new_df[categorical_columns] = new_df[categorical_columns].astype('int64')

    for col in std_df.columns:
        new_df[col] = std_df[col]

    if not return_scaler:
        return new_df
    return new_df, X_scaler, y_scaler

def feature_engineer_prediction(X_data: pd.DataFrame,
                                X_scaler: StandardScaler,
                                reset_index: bool=False) -> pd.DataFrame:
    """
    Perform feature engineering on the input data, including scaling numeric features,
    one-hot encoding categorical features, and resetting the index if specified.

    Parameters
    ----------
    X_data : pd.DataFrame
        The input data containing both numeric and categorical features. It must 
        not include the target variable 'Employee_Satisfaction_Score'.

    X_scaler : StandardScaler
        A fitted StandardScaler instance used for scaling the numeric features.

    reset_index : bool, default=False
        Whether to reset the index of the resulting DataFrame. If True, the index 
        will be reset and the old index will be discarded.

    Returns
    -------
    pd.DataFrame
        A DataFrame with the processed features, including scaled numeric features,
        one-hot encoded categorical features, and optionally with the index reset.
        
    Raises
    ------
    IndexError
        If the input data contains the target variable 'Employee_Satisfaction_Score'.
    """
    if 'Employee_Satisfaction_Score' in X_data.columns:
        raise IndexError("The target `Employee_Satisfaction_Score`"
                         "is being added as feature variable.")
    
    numeric_columns = get_features()['numeric_columns']

    def scale_data(columns: list,
                   sub_scaler: StandardScaler=None):
        if sub_scaler is None:
            sub_scaler = StandardScaler()
            std_values = sub_scaler.fit_transform(X_data[columns])
        else:
            std_values = sub_scaler.transform(X_data[columns])
        return (std_values, sub_scaler)

    X_std_values, X_scaler = scale_data(numeric_columns, X_scaler)

    std_df = pd.DataFrame(X_std_values,
                          columns=numeric_columns)

    new_df = one_hot_encode(
        X_data,
        get_features()['one_hot_encode_columns']
    )

    if reset_index:
        new_df.reset_index(inplace=True,
                           drop=True)

    categorical_columns = new_df.select_dtypes(
        include=['int', 'int64']
    ).columns
    new_df[categorical_columns] = new_df[categorical_columns].astype('int64')

    for col in std_df.columns:
        new_df[col] = std_df[col]

    return new_df

def feature_engineered_employee_performance(
        data_df: pd.DataFrame=None,
        X_data: pd.DataFrame=None,
        X_scaler: StandardScaler = None,
        y_scaler: StandardScaler = None,
        reset_index: bool = False,
        return_scaler: bool = False
    ) -> tuple[pd.DataFrame, StandardScaler,
               StandardScaler] | pd.DataFrame:
    """
    Feature engineer the HR Performance dataset by scaling numeric features, 
    handling categorical features, and optionally returning the scalers.

    Parameters
    ----------
    data_df : pd.DataFrame, optional
        The input dataset containing employee performance data. If provided, 
        this will be used for feature engineering.

    X_data : pd.DataFrame, optional
        The input dataset with feature data. If `data_df` is not provided, 
        `X_data` must be passed.

    X_scaler : StandardScaler, optional
        A pre-fitted scaler for transforming the numeric features of `X_data`. 
        If `None`, a new scaler is trained using the data.

    y_scaler : StandardScaler, optional
        A pre-fitted scaler for transforming the target variable (if applicable). 
        If `None`, a new scaler is trained using the target variable.

    reset_index : bool, optional, default=False
        Whether to reset the index of the returned DataFrame. If True, the 
        index will be reset and the old index will be discarded.

    return_scaler : bool, optional, default=False
        If True, returns both the transformed DataFrame and the scaler(s) 
        (i.e., the fitted `X_scaler` and `y_scaler`).

    Returns
    -------
    pd.DataFrame
        The transformed dataset after feature engineering, with scaling applied to 
        the numeric features and one-hot encoding applied to categorical features.
        Optionally, the index will be reset if `reset_index=True`.

    tuple(pd.DataFrame, StandardScaler, StandardScaler)
        If `return_scaler=True`, the function returns a tuple containing the 
        transformed DataFrame along with the fitted `X_scaler` and `y_scaler`.
        
    Raises
    ------
    ValueError
        If neither `data_df` nor `X_data` is provided, or if both are provided.
    """
    if data_df is None and X_data is None:
        raise ValueError("No data input found for feature engineering.")
    if data_df is not None and X_data is not None:
        raise ValueError("Two data inputs found. Please select only one input type.")
    elif data_df is not None and X_data is None:
        return feature_training(data_df=data_df,
                         reset_index=reset_index,
                         return_scaler=return_scaler)
    elif data_df is None and X_data is not None:
        return feature_engineer_prediction(X_data=X_data,
                                    X_scaler=X_scaler,
                                    reset_index=reset_index)
    
=======
        mlflow.log_artifact(file_path)
>>>>>>> 38f7301eacf189707bccdbb04b8b886cd97620ad

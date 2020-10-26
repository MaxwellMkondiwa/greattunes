import torch
import pytest
from creative_project._max_response import find_max_response_value


def test_find_max_response_value_unit(custom_models_simple_training_data_4elements):
    """
    test finding of max response value
    """

    # data -- max at 4th element
    train_X = custom_models_simple_training_data_4elements[0]
    train_Y = custom_models_simple_training_data_4elements[1]

    max_X, max_Y = find_max_response_value(train_X, train_Y)

    # assert that max value is at index 3 (4th element)
    maxit = 3
    assert max_X[0].item() == train_X[maxit].item()
    assert max_Y[0].item() == train_Y[maxit].item()


def test_find_max_response_value_multivariate(training_data_covar_complex):
    """
    test that the right covariate row tensor is returned when train_X is multivariate
    """

    # data
    train_X = training_data_covar_complex[1]
    train_Y = training_data_covar_complex[2]

    max_X, max_Y = find_max_response_value(train_X, train_Y)

    # assert that max value is at index 1 (2nd element)
    maxit = 1
    for it in range(train_X.shape[1]):
        assert max_X[it].item() == train_X[maxit, it].item()
    assert max_Y[0].item() == train_Y[maxit].item()
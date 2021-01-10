import torch
import numpy as np


class Validators:
    """
    validator functions used to initialize data structures etc. These functions are to remain private, i.e.
    non-accessible to the user.

    These methods are kept in a separate class to maintain that they be private in the main
    class (that class being defined in __init__.py.
    """

    def __validate_training_data(self, train_X, train_Y):
        """
        validate provided training data is of compatible length
        :parameter train_X (torch.tensor, size: batch_shape X num_obs X num_training_features OR num_obs X
        num_training_features)
        :parameter train_Y (torch.tensor, size batch_shape X num_obs X num_output_models [allows for batched models]
        OR num_obs X num_output_models)
        :return valid (bool)
        """

        valid = False

        # validate training data present
        if (train_X is not None) & (train_Y is not None):

            # validate data type (tensors are set to type torch.DoubleTensor by setting dtype=torch.double)
            if isinstance(train_X, torch.DoubleTensor) & isinstance(
                train_Y, torch.DoubleTensor
            ):

                # validate same number of rows
                if train_X.shape[0] == train_Y.shape[0]:

                    # validate train_X number of covariates correspond to covars
                    if self.__validate_num_covars(
                        train_X
                    ):  # train_X.shape[0] == self.initial_guess.shape[0]:

                        valid = True

        return valid

    def __validate_num_covars(self, covars_array):
        """
        validate that entries in "covars_array" is equal to number of covars provided to "covars" during
        class instance initialization of CreativeProject (from creative_project.__init__.py)
        :param covars_array (torch.tensor, pandas dataframe, numpy array; shape needs to be
        num_observations X num_covariates)
        :param
            - state of initialized class:
                - self.initial_guess (torch.tensor)
        :return valid (bool)
        """

        valid = False

        # with one column per covariate in covars_array, and one column per covariate in initial_guess, makes sure that
        # same amount of covariates present in both
        if covars_array is not None:
            if len(covars_array.shape) > 1:
                if covars_array.shape[1] == self.initial_guess.shape[1]:
                    valid = True

        return valid

    def __validate_covars(self, covars):
        """
        validate that covars is a list of tuples of floats
        :param covars: object, only accepted if covars is list of tuples of floats
        :return: valid (bool
        """

        valid = False

        if covars is None:
            raise ValueError(
                "kre8_core.creative_project._validators.Validator.__validate_covars: covars is None"
            )

        if not isinstance(covars, list):
            raise TypeError(
                "kre8_core.creative_project._validators.Validator.__validate_covars: covars is not list "
                "of tuples (not list)"
            )

        for entry in covars:
            if not isinstance(entry, tuple):
                raise TypeError(
                    "kre8_core.creative_project._validators.Validator.__validate_covars: entry in covars list is not "
                    "tuple"
                )

        for entry in covars:
            for el in entry:
                if not isinstance(el, (float, int)):
                    raise TypeError(
                        "kre8_core.creative_project._validators.Validator.__validate_covars: tuple element "
                        + str(el)
                        + " in covars list is neither of type float or int"
                    )

        valid = True

        return valid

    def __validate_num_response(self, response_array):
        """
        validate that there is only one response per timepoint in "response_array"
        :param covars_array (torch.tensor, pandas dataframe, numpy array; shape needs to be
        num_observations X num_covariates)
        :return valid (bool)
        """

        valid = False

        # make sure single column
        if response_array is not None:
            if len(response_array.shape) > 1:
                if response_array.shape[1] == 1:
                    valid = True

        return valid

    def __continue_iterating_rel_tol_conditions(self, rel_tol, rel_tol_steps):
        """
        determine whether 'rel_tol'-conditions are satisfied by comparing the best candidate (self.best_response_value)
        at this and previous steps. In case the 'rel_tol'-conditions are met, this method returns false.

        The 'rel_tol'-conditions for stopping are:
            - 'rel_tol' and 'rel_tol_steps' are both None: nothing happens, and this method returns True at all
            iterations
            - 'rel_tol' is not None and 'rel_tol_steps' is None: in this case, stop at the first iteration where the
            relative difference between self.best_response_value at this and the preceding iteration are below the
            value set by 'rel_tol' (stop by returning False)
            -  'rel_tol' is not None and 'rel_tol_steps' is not None: stop when the relative difference of
            self.best_response_value at the current and the 'rel_tol_steps' preceding steps are all below 'rel_tol'
            (return False)

        :param rel_tol (float): limit of relative difference of self.best_response_value taken as convergence
        :param rel_tol_steps (int): number of consecutive steps in which the improvement in self.best_response_value
        is below 'rel_tol' before stopping
        :return: continue_iterating (bool)
        """

        continue_iterating = True

        if (rel_tol is not None) & (rel_tol_steps is None):

            # leverage the functionality built for rel_tol_steps > 1
            rel_tol_steps = 1

        if (rel_tol is not None) & (rel_tol_steps is not None):

            # only proceed if at least 'rel_tol_steps' iterations have been completed
            if self.best_response_value.size()[0] >= rel_tol_steps:

                # build list of relative differences

                # first build tensor with the last rel_tol_steps entries in self.best_response_value and the last
                # rel_tol_steps+1 entries
                tmp_array = torch.cat(
                    (self.best_response_value[-(rel_tol_steps+1):-1], self.best_response_value[-(rel_tol_steps):]),
                    dim=1).numpy()

                # calculate the relative differences
                tmp_rel_diff = np.diff(tmp_array, axis=1) / self.best_response_value[-(rel_tol_steps):].numpy()

                # determine if all below 'rel_tol'
                below_rel_tol = [rel_dif[0] < rel_tol for rel_dif in tmp_rel_diff.tolist()]

                # only accept if the relative difference is below 'rel_tol' for all steps
                if sum(below_rel_tol) == rel_tol_steps:
                    continue_iterating = False

        return continue_iterating

#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import timedelta
import numpy as np
import pandas as pd
from covsirphy.util.error import EmptyError
from covsirphy.util.validator import Validator
from covsirphy.util.term import Term
from covsirphy.dynamics.ode import ODEModel


class Dynamics(Term):
    """Class to hand phase-dependent SIR-derived ODE models.

    Args:
        model (covsirphy.ODEModel): definition of ODE model
        date_range (tuple of (str, str)): start date and end date of dynamics to analyze
        tau (int or None): tau value [min] or None (set later with data)
        name (str or None): name of dynamics to show in figures (e.g. "baseline") or None (un-set)
    """
    _PH = "Phase_ID"
    _SIFR = [Term.S, Term.CI, Term.F, Term.R]

    def __init__(self, model, date_range, tau=None, name=None):
        self._model = Validator(model, "model", accept_none=False).subclass(ODEModel)
        first_date, last_date = Validator(date_range, "date_range", accept_none=False).sequence(length=2)
        self._first = Validator(first_date, name="the first value of @date_range", accept_none=False).date()
        self._last = Validator(
            last_date, name="the second date of @date_range", accept_none=False).date(value_range=(self._first, None))
        self._tau = Validator(tau, "tau", accept_none=True).tau()
        self._name = None if name is None else Validator(name, "name").instance(str)
        # Index: Date, Columns: S, I, F, R, ODE parameters
        self._parameters = self._model._PARAMETERS[:]
        self._df = pd.DataFrame(
            {self._PH: 0}, index=pd.date_range(start=self._first, end=self._last, freq="D"),
            columns=[self._PH, *self._SIFR, *self._parameters])

    @property
    def name(self):
        """str: name of dynamics to show in figures (e.g. "baseline") or None (un-set)
        """
        return self._name

    @name.setter
    def name(self, name):
        self._name = Validator(name, "name").instance(str)

    @name.deleter
    def name(self):
        self._name = None

    @classmethod
    def from_sample(cls, model, date_range=None, tau=1440):
        """Initialize model with sample data of one-phase ODE model.

        Args:
            date_range (tuple(str or None, str or None) or None): start date and end date of simulation
            tau (int): tau value [min]

        Returns:
            covsirphy.ODEModel: initialized model

        Note:
            Regarding @date_range, refer to covsirphy.ODEModel.from_sample().
        """
        Validator(model, "model", accept_none=False).subclass(ODEModel)
        model_instance = model.from_sample(date_range=date_range, tau=tau)
        settings_dict = model_instance.settings()
        variable_df = model.inverse_transform(model_instance.solve()).iloc[[0]]
        param_df = pd.DataFrame(settings_dict["param_dict"], index=[pd.to_datetime(settings_dict["date_range"][0])])
        param_df.index.name = cls.DATE
        df = pd.concat([variable_df, param_df], axis=1)
        instance = cls(model=model, date_range=settings_dict["date_range"], tau=tau, name="Sample data")
        instance.register(data=df.reset_index())
        return instance

    def register(self, data=None):
        """Register data to get initial values and ODE parameter values (if available).

        Args:
            data (pandas.DataFrame or None): new data to overwrite the current information
                Index
                    reset index
                Columns
                    - Date (pandas.Timestamp): Observation date
                    - Susceptible (int): the number of susceptible cases
                    - Infected (int): the number of currently infected cases
                    - Fatal (int): the number of fatal cases
                    - Recovered (int): the number of recovered cases
                    - (numpy.float64): ODE parameter values defined with model.PARAMETERS

        Returns:
            pandas.DataFrame: the current information
                Index
                    reset index
                Columns
                    - Date (pandas.Timestamp): Observation date
                    - Susceptible (int): the number of susceptible cases
                    - Infected (int): the number of currently infected cases
                    - Fatal (int): the number of fatal cases
                    - Recovered (int): the number of recovered cases
                    - (numpy.float64): ODE parameter values defined with model.PARAMETERS

        Note:
            Change points of ODE parameter values will be recognized as the change points of phases.

        Note:
            NA can used in the newer phases because filled with that of the older phases.
        """
        if data is not None:
            all_df = self._df.copy()
            new_df = Validator(data, "data").dataframe(columns=[self.DATE])
            new_df.index = pd.to_datetime(new_df[self.DATE]).dt.round("D")
            all_df.loc[:] = np.nan
            all_df[self._PH] = 0
            all_df.update(new_df)
            if all_df.loc[self._first, self._SIFR].isna().any():
                raise EmptyError(
                    f"records on {self._first.strftime(self.DATE_FORMAT)}", details="Records must be registered for simulation")
            all_df.index.name = self.DATE
            self._df = all_df.convert_dtypes()
            # Find change points with parameter values
            param_df = all_df.loc[:, self._parameters].dropna(how="all", axis=0).ffill()
            self.segment(points=param_df.index.tolist(), overwrite=True)
        return self._df.reset_index().loc[:, [self.DATE, *self._SIFR, *self._parameters]]

    def segment(self, points, overwrite=False):
        """Perform time-series segmentation with points.

        Args:
            points (list[str]): dates of change points
            overwrite (bool): whether remove all phases before segmentation or not

        Returns:
            covsirphy.Dynamics: self

        Note:
            @points can include the first date, but not required.

        Note:
            @points must be selected from the first date to three days before the last date specified covsirphy.Dynamics(date_range).
        """
        candidates = pd.date_range(start=self._first, end=self._last - timedelta(days=2), freq="D")
        change_points = Validator(points, "points", accept_none=False).sequence(unique=True, candidates=candidates)
        df = self._df.copy()
        if overwrite:
            df[self._PH] = 0
        for point in change_points:
            df.loc[point:, self._PH] += 1
        self._df = df.convert_dtypes()
        return self

    def summary(self):
        """Summarize phase information.

        Returns:
            pandas.DataFrame
                Index
                    Phase (str): phase names, 0th, 1st,...
                Columns
                    - Start (pandas.Timestamp): start date of the phase
                    - End (pandas.Timestamp): end date of the phase
                    - Population (numpy.Int64): population value of the start date
                    - ODE (str): ODE model names, like "SIR"
                    - (float): estimated parameter values, including rho
                    - tau (int): tau value [min]
                    - If available,
                        - Rt (float): phase-dependent reproduction number
                        - (int or float): day parameters, including 1/beta [days]
                        - {metric}: score with the estimated parameter values
                        - Trials (int): the number of trials
                        - Runtime (str): runtime of optimization
        """
        df = self._df.reset_index()
        df[self._PH], _ = df[self._PH].factorize()
        first_df = df.groupby(self._PH).first()
        df = first_df.join(df.groupby(self._PH).last(), rsuffix="_last")
        df = df.rename(columns={self.DATE: self.START, f"{self.DATE}_last": self.END})
        df = df.loc[:, [col for col in df.columns if "_last" not in col]]
        df.index.name = self.PHASE
        df.index = [self.num2str(num) for num in df.index]
        # ODE model and tau value
        df[self.ODE] = self._model._NAME.replace(" Model", "")
        df[self.TAU] = self._tau
        # Calculate population values
        df[self.N] = df[self._SIFR].sum(axis=1).replace(0, np.nan)
        # Reproduction number
        df[self.RT] = 0
        # Set the order of columns
        fixed_cols = [
            self.START, self.END, self.N, self.RT, *self._model._PARAMETERS, self.TAU, *self._model._DAY_PARAMETERS]
        others = [col for col in df.columns if col not in set(fixed_cols) | set(self._SIFR)]
        return df.reindex(columns=[*fixed_cols, *others]).dropna(how="all", axis=1).ffill().convert_dtypes()

    def simulate(self, model_specific=False):
        """Perform simulation with phase-dependent ODE model.

        Args:
            model_specific (bool): whether convert S, I, F, R to model-specific variables or not

        Returns:
            pandas.DataFrame:
                Index
                    reset index
                Columns
                    - Date (pd.Timestamp): Observation date
                    - if @model_specific is False:
                        - Susceptible (int): the number of susceptible cases
                        - Infected (int): the number of currently infected cases
                        - Fatal (int): the number of fatal cases
                        - Recovered (int): the number of recovered cases
                    - if @model_specific is True, variables defined by model.VARIABLES of covsirphy.Dynamics(model)
        """
        all_df = self._df.copy()
        all_df[self._PH], _ = all_df[self._PH].factorize()
        date_groupby = all_df.reset_index().groupby(self._PH)
        start_dates = date_groupby.first()[self.DATE].sort_values()
        end_dates = date_groupby.last()[self.DATE].sort_values()
        variables, parameters = self._model._VARIABLES[:], self._model._PARAMETERS[:]
        param_df = all_df.ffill().loc[:, parameters]
        # Simulation
        dataframes = []
        for (start, end) in zip(start_dates, end_dates):
            variable_df = all_df.loc[start: end + timedelta(days=1), variables]
            if variable_df.iloc[0].isna().any():
                variable_df = pd.DataFrame(
                    index=pd.date_range(start, end + timedelta(days=1), freq="D"), columns=self._SIFR)
                variable_df.update(self._model.inverse_transform(dataframes[-1]))
            variable_df.index.name = self.DATE
            param_dict = param_df.loc[start].to_dict()
            instance = self._model.from_data(data=variable_df.reset_index(), param_dict=param_dict, tau=self._tau)
            dataframes.append(instance.solve())
        # Combine results of phases
        df = pd.concat(dataframes, axis=0).drop_duplicates(keep="first").loc[self._first: self._last]
        if model_specific:
            return df.reset_index().convert_dtypes()
        df = self._model.inverse_transform(data=df)
        df.index.name = self.DATE
        return df.reset_index().convert_dtypes()

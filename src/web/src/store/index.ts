/**
 * Redux store configuration file that implements a dynamic reducer registry pattern to avoid circular dependencies.
 * It exports the configured store along with TypeScript types and hooks for use throughout the application.
 * 
 * @packageDocumentation
 * @module store
 * @version 1.0.0
 */

import {
  configureStore,
  combineReducers,
  ReducersMapObject,
  Reducer,
  AnyAction,
  CombinedState
} from '@reduxjs/toolkit'; //  ^1.9.5
import {
  useDispatch,
  useSelector,
  TypedUseSelectorHook
} from 'react-redux'; //  ^8.1.1
import authReducer from './auth/authSlice';
import integrationsReducer from './integrations/integrationsSlice';
import organizationsReducer from './organizations/organizationsSlice';
import ratesReducer from './rates/ratesSlice';
import { OrganizationsState } from './organizations/organizationsSlice';
import { AuthState } from '../types/auth';
import { IntegrationsState } from './integrations/integrationsSlice';
import { RateState } from './rates/ratesSlice';

/**
 * Type definition for the root state of the Redux store, combining all slice states.
 */
export type RootState = CombinedState<{
  auth: AuthState;
  organizations: OrganizationsState;
  integrations: IntegrationsState;
  rates: RateState;
}>;

/**
 * Type definition for the Redux dispatch function.
 */
export type AppDispatch = ReturnType<typeof configureAppStore>['dispatch'];

/**
 * Creates a reducer manager that can dynamically add and remove reducers
 * @param initialReducers - Object containing initial reducers
 * @returns Reducer manager with getReducerMap, reduce, add, and remove methods
 */
function createReducerManager(initialReducers: ReducersMapObject) {
  // Initialize reducers with the passed initial reducers
  let reducers = { ...initialReducers };

  // Create combined reducer using combineReducers
  let combinedReducer = combineReducers(reducers);

  // Define getReducerMap function to return current reducers
  let reducerMap = { ...reducers };

  // Define reduce function to handle state updates
  return {
    getReducerMap: () => reducerMap,
    reduce: (state: RootState | undefined, action: AnyAction) => {
      if (action.type === 'RESET_ALL_STATE') {
        state = undefined;
      }
      return combinedReducer(state, action);
    },
    add: (key: string, reducer: Reducer) => {
      if (!key || reducerMap[key]) {
        return;
      }

      // Add the reducer to the reducer map
      reducers[key] = reducer;
      reducerMap = { ...reducers };

      // Update the combined reducer
      combinedReducer = combineReducers(reducers);
    },
    remove: (key: string) => {
      if (!key || !reducerMap[key]) {
        return;
      }

      // Remove the reducer from the reducer map
      delete reducers[key];
      reducerMap = { ...reducers };

      // Update the combined reducer
      combinedReducer = combineReducers(reducers);
    }
  };
}

/**
 * Configures the Redux store with initial reducers and creates a reducer manager
 * @returns Configured store with additional reducerManager property
 */
function configureAppStore() {
  // Create initial reducers object with base reducers that don't cause circular dependencies
  const initialReducers: ReducersMapObject<RootState> = {
    auth: authReducer,
    organizations: organizationsReducer,
    integrations: integrationsReducer,
    rates: ratesReducer,
  };

  // Create reducer manager with initial reducers
  const reducerManager = createReducerManager(initialReducers);

  // Configure store with reducer manager's reduce function
  const store = configureStore({
    reducer: reducerManager.reduce as Reducer<RootState>,
    devTools: process.env.NODE_ENV !== 'production',
    middleware: (getDefaultMiddleware) => getDefaultMiddleware({
      serializableCheck: false,
    }),
  });

  // Add reducerManager to store object
  (store as any).reducerManager = reducerManager;

  // Return enhanced store
  return store;
}

/**
 * Configured Redux store with all reducers and middleware
 */
export const store = configureAppStore();

/**
 * Custom typed hook for dispatching Redux actions with correct TypeScript types
 * @returns Typed dispatch function for the Redux store
 */
export const useAppDispatch: () => AppDispatch = useDispatch;

/**
 * Custom typed hook for selecting data from the Redux state with correct TypeScript types
 * @returns Typed selector function for accessing the Redux state
 */
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;
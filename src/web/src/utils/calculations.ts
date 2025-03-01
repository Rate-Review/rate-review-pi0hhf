/**
 * Utility functions for calculations related to rate negotiations, impact analysis,
 * and analytics throughout the Justice Bid application.
 *
 * These functions support core requirements for rate impact analysis, multi-currency
 * calculations, and comparative analytics needed throughout the rate negotiation process.
 *
 * @version 1.0.0
 */

import { Rate, RateHistory } from '../types/rate';
import { BillingData } from '../types/analytics';
import { convertCurrency } from './currency';
import { dateRangeOverlap } from './date';

/**
 * Calculates the percentage increase between two rate values
 * 
 * @param currentRate - The current/baseline rate amount
 * @param proposedRate - The proposed/new rate amount
 * @returns Percentage increase as a decimal (e.g., 0.05 for 5%)
 */
export function calculateRateIncrease(currentRate: number, proposedRate: number): number {
  // Check for zero or negative current rate to avoid division by zero or negative percentage
  if (currentRate <= 0) {
    return 1; // 100% increase as a fallback value
  }

  // Calculate percentage increase
  const increase = (proposedRate - currentRate) / currentRate;
  
  return increase;
}

/**
 * Calculates the financial impact of rate changes based on historical hours
 * 
 * @param currentRates - Array of current rates
 * @param proposedRates - Array of proposed rates
 * @param billingHistory - Historical billing data to calculate impact
 * @returns Object containing total impact, percentage impact, and impact breakdowns
 */
export function calculateRateImpact(
  currentRates: Rate[],
  proposedRates: Rate[],
  billingHistory: BillingData[]
): {
  totalImpact: number;
  percentageImpact: number;
  impactByAttorney: Record<string, number>;
  impactByStaffClass: Record<string, number>;
} {
  // Create maps for easier lookup
  const currentRateMap = new Map<string, Rate>();
  const proposedRateMap = new Map<string, Rate>();
  
  // Populate maps with attorney ID as key
  currentRates.forEach(rate => currentRateMap.set(rate.attorneyId, rate));
  proposedRates.forEach(rate => proposedRateMap.set(rate.attorneyId, rate));
  
  // Initialize tracking variables
  let totalCurrentCost = 0;
  let totalProposedCost = 0;
  const impactByAttorney: Record<string, number> = {};
  const impactByStaffClass: Record<string, number> = {};
  
  // Process each billing history entry
  billingHistory.forEach(entry => {
    const currentRate = currentRateMap.get(entry.attorneyId);
    const proposedRate = proposedRateMap.get(entry.attorneyId);
    
    // Skip if we don't have both rates for comparison
    if (!currentRate || !proposedRate) {
      return;
    }
    
    // Calculate costs with current and proposed rates
    const currentCost = entry.hours * currentRate.amount;
    const proposedCost = entry.hours * proposedRate.amount;
    const impact = proposedCost - currentCost;
    
    // Update totals
    totalCurrentCost += currentCost;
    totalProposedCost += proposedCost;
    
    // Update impact by attorney
    impactByAttorney[entry.attorneyId] = (impactByAttorney[entry.attorneyId] || 0) + impact;
    
    // Update impact by staff class
    if (currentRate.staffClassId) {
      impactByStaffClass[currentRate.staffClassId] = 
        (impactByStaffClass[currentRate.staffClassId] || 0) + impact;
    }
  });
  
  // Calculate total impact and percentage
  const totalImpact = totalProposedCost - totalCurrentCost;
  const percentageImpact = totalCurrentCost > 0 ? totalImpact / totalCurrentCost : 0;
  
  return {
    totalImpact,
    percentageImpact,
    impactByAttorney,
    impactByStaffClass
  };
}

/**
 * Compares rates or increases against a peer group
 * 
 * @param targetValues - Array of values to compare (e.g., proposed rate increases)
 * @param peerValues - Array of peer values for comparison
 * @returns Statistical comparison metrics
 */
export function calculatePeerComparison(
  targetValues: number[],
  peerValues: number[]
): {
  average: number;
  median: number;
  percentile: number;
  range: { min: number; max: number };
} {
  // Calculate target average
  const targetAverage = targetValues.length > 0 
    ? targetValues.reduce((sum, val) => sum + val, 0) / targetValues.length 
    : 0;
  
  // If no peer values, return default result
  if (!peerValues.length) {
    return {
      average: 0,
      median: 0,
      percentile: 0,
      range: { min: 0, max: 0 }
    };
  }
  
  // Calculate peer average
  const peerAverage = peerValues.reduce((sum, val) => sum + val, 0) / peerValues.length;
  
  // Sort peer values for median and range calculations
  const sortedPeerValues = [...peerValues].sort((a, b) => a - b);
  
  // Calculate median
  const midIndex = Math.floor(sortedPeerValues.length / 2);
  const median = sortedPeerValues.length % 2 === 0
    ? (sortedPeerValues[midIndex - 1] + sortedPeerValues[midIndex]) / 2
    : sortedPeerValues[midIndex];
  
  // Calculate range
  const min = sortedPeerValues[0];
  const max = sortedPeerValues[sortedPeerValues.length - 1];
  
  // Calculate percentile of target average within peer group
  let percentile = 0;
  
  // Count how many peer values are less than target average
  const countLessThan = sortedPeerValues.filter(val => val < targetAverage).length;
  
  if (sortedPeerValues.length > 0) {
    percentile = (countLessThan / sortedPeerValues.length) * 100;
  }
  
  return {
    average: peerAverage,
    median,
    percentile,
    range: { min, max }
  };
}

/**
 * Calculates a weighted average based on values and their weights
 * 
 * @param values - Array of values to average
 * @param weights - Array of weights corresponding to each value
 * @returns The weighted average
 */
export function calculateWeightedAverage(values: number[], weights: number[]): number {
  // Validate input arrays have the same length
  if (values.length !== weights.length) {
    throw new Error('Values and weights arrays must have the same length');
  }
  
  // Handle empty arrays
  if (values.length === 0) {
    return 0;
  }
  
  // Calculate sum of values multiplied by weights
  let weightedSum = 0;
  let weightSum = 0;
  
  for (let i = 0; i < values.length; i++) {
    weightedSum += values[i] * weights[i];
    weightSum += weights[i];
  }
  
  // Return the weighted average, or 0 if sum of weights is 0
  return weightSum > 0 ? weightedSum / weightSum : 0;
}

/**
 * Calculates average rates by staff class from a collection of rates
 * 
 * @param rates - Array of rates to analyze
 * @returns Map of staff class IDs to their average rates
 */
export function calculateAverageRatesByStaffClass(rates: Rate[]): Record<string, number> {
  const staffClassRates: Record<string, number[]> = {};
  
  // Group rates by staff class
  rates.forEach(rate => {
    if (rate.staffClassId) {
      if (!staffClassRates[rate.staffClassId]) {
        staffClassRates[rate.staffClassId] = [];
      }
      staffClassRates[rate.staffClassId].push(rate.amount);
    }
  });
  
  // Calculate average for each staff class
  const averages: Record<string, number> = {};
  
  Object.entries(staffClassRates).forEach(([staffClassId, rates]) => {
    const sum = rates.reduce((total, rate) => total + rate, 0);
    averages[staffClassId] = rates.length > 0 ? sum / rates.length : 0;
  });
  
  return averages;
}

/**
 * Analyzes historical rate trends over time
 * 
 * @param rateHistory - Array of historical rate data
 * @param groupBy - Dimension to group by (attorney, staff class, etc.)
 * @returns Trend analysis results including CAGR and average increases
 */
export function calculateHistoricalTrend(
  rateHistory: RateHistory[],
  groupBy: string
): {
  trends: Record<string, number[]>;
  cagr: Record<string, number>;
  averageIncrease: Record<string, number>;
} {
  // Group rate history by the specified dimension
  const groupedHistory: Record<string, RateHistory[]> = {};
  
  rateHistory.forEach(history => {
    let groupKey: string;
    
    // Determine the group key based on groupBy parameter
    switch (groupBy) {
      case 'attorney':
        groupKey = history.attorneyId;
        break;
      case 'staffClass':
        groupKey = history.staffClassId || 'unknown';
        break;
      case 'firm':
        groupKey = history.firmId;
        break;
      default:
        groupKey = 'all';
    }
    
    if (!groupedHistory[groupKey]) {
      groupedHistory[groupKey] = [];
    }
    
    groupedHistory[groupKey].push(history);
  });
  
  // Calculate trends for each group
  const trends: Record<string, number[]> = {};
  const cagr: Record<string, number> = {};
  const averageIncrease: Record<string, number> = {};
  
  Object.entries(groupedHistory).forEach(([groupKey, histories]) => {
    // Sort by effective date
    const sortedHistory = [...histories].sort(
      (a, b) => new Date(a.effectiveDate).getTime() - new Date(b.effectiveDate).getTime()
    );
    
    // Extract rate values in chronological order
    const rateValues = sortedHistory.map(h => h.amount);
    trends[groupKey] = rateValues;
    
    // Calculate year-over-year increases
    const increases: number[] = [];
    for (let i = 1; i < sortedHistory.length; i++) {
      const prevAmount = sortedHistory[i - 1].amount;
      const currentAmount = sortedHistory[i].amount;
      
      if (prevAmount > 0) {
        increases.push((currentAmount - prevAmount) / prevAmount);
      }
    }
    
    // Calculate average annual increase
    averageIncrease[groupKey] = increases.length > 0 
      ? increases.reduce((sum, inc) => sum + inc, 0) / increases.length 
      : 0;
    
    // Calculate CAGR if we have at least start and end points
    if (sortedHistory.length >= 2) {
      const startValue = sortedHistory[0].amount;
      const endValue = sortedHistory[sortedHistory.length - 1].amount;
      const startDate = new Date(sortedHistory[0].effectiveDate);
      const endDate = new Date(sortedHistory[sortedHistory.length - 1].effectiveDate);
      
      // Calculate years between start and end dates
      const years = (endDate.getTime() - startDate.getTime()) / (365.25 * 24 * 60 * 60 * 1000);
      
      if (years > 0 && startValue > 0) {
        // CAGR formula: (endValue / startValue)^(1/years) - 1
        cagr[groupKey] = Math.pow(endValue / startValue, 1 / years) - 1;
      } else {
        cagr[groupKey] = 0;
      }
    } else {
      cagr[groupKey] = 0;
    }
  });
  
  return {
    trends,
    cagr,
    averageIncrease
  };
}

/**
 * Calculates the effective rate for a given period considering rate changes
 * 
 * @param rates - Array of rates potentially applicable to the period
 * @param startDate - Start date of the period
 * @param endDate - End date of the period
 * @returns The effective weighted rate for the period
 */
export function calculateEffectiveRate(
  rates: Rate[],
  startDate: Date,
  endDate: Date
): number {
  // Filter rates to those effective within the given period
  const applicableRates = rates.filter(rate => {
    const rateStart = new Date(rate.effectiveDate);
    const rateEnd = rate.expirationDate ? new Date(rate.expirationDate) : new Date(8640000000000000); // Far future date
    
    return dateRangeOverlap(
      rateStart,
      rateEnd,
      startDate,
      endDate
    );
  });
  
  if (applicableRates.length === 0) {
    return 0;
  }
  
  // If only one rate applies to the entire period, return it directly
  if (applicableRates.length === 1) {
    return applicableRates[0].amount;
  }
  
  // For multiple rates, calculate weighted average based on effective days
  const periodDays = (endDate.getTime() - startDate.getTime()) / (24 * 60 * 60 * 1000);
  const weightedRates: number[] = [];
  const weights: number[] = [];
  
  applicableRates.forEach(rate => {
    const rateStart = new Date(rate.effectiveDate);
    const rateEnd = rate.expirationDate ? new Date(rate.expirationDate) : new Date(8640000000000000);
    
    // Calculate effective start and end dates within the period
    const effectiveStart = rateStart < startDate ? startDate : rateStart;
    const effectiveEnd = rateEnd > endDate ? endDate : rateEnd;
    
    // Calculate effective days and weight
    const effectiveDays = (effectiveEnd.getTime() - effectiveStart.getTime()) / (24 * 60 * 60 * 1000);
    const weight = effectiveDays / periodDays;
    
    weightedRates.push(rate.amount);
    weights.push(weight);
  });
  
  // Calculate weighted average
  return calculateWeightedAverage(weightedRates, weights);
}

/**
 * Normalizes rates to a single currency for comparison
 * 
 * @param rates - Array of rates potentially in different currencies
 * @param targetCurrency - Currency to normalize to
 * @returns Array of rates with amounts normalized to the target currency
 */
export function normalizeRatesByCurrency(
  rates: Rate[],
  targetCurrency: string
): Rate[] {
  // Create a deep copy to avoid mutating the original rates
  const normalizedRates = JSON.parse(JSON.stringify(rates)) as Rate[];
  
  // Get exchange rates (would need to be passed or fetched in a real implementation)
  // For this utility, we'll assume exchange rates are available
  const exchangeRates: Record<string, number> = {};
  
  // Normalize each rate to the target currency
  return normalizedRates.map(rate => {
    // Only convert if currencies differ
    if (rate.currency !== targetCurrency) {
      // Create a new rate object with the converted amount
      const convertedRate = {
        ...rate,
        amount: convertCurrency(rate.amount, rate.currency, targetCurrency, exchangeRates),
        currency: targetCurrency
      };
      return convertedRate;
    }
    return rate;
  });
}
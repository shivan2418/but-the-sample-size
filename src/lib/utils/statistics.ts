/**
 * Statistical utility functions for sample size demonstrations
 */

/**
 * Calculate margin of error for a proportion
 * MOE = z * sqrt(p(1-p)/n) where z = 1.96 for 95% confidence
 */
export function marginOfError(sampleSize: number, proportion = 0.5, confidenceLevel = 0.95): number {
	const z = getZScore(confidenceLevel);
	return z * Math.sqrt((proportion * (1 - proportion)) / sampleSize);
}

/**
 * Get z-score for a given confidence level
 */
export function getZScore(confidenceLevel: number): number {
	const zScores: Record<number, number> = {
		0.9: 1.645,
		0.95: 1.96,
		0.99: 2.576
	};
	return zScores[confidenceLevel] || 1.96;
}

/**
 * Calculate required sample size for a given margin of error
 * n = (z^2 * p(1-p)) / MOE^2
 */
export function requiredSampleSize(
	targetMOE: number,
	proportion = 0.5,
	confidenceLevel = 0.95
): number {
	const z = getZScore(confidenceLevel);
	return Math.ceil((z * z * proportion * (1 - proportion)) / (targetMOE * targetMOE));
}

/**
 * Finite population correction factor
 * FPC = sqrt((N - n) / (N - 1))
 * Only matters when n/N > 0.05
 */
export function finitePopulationCorrection(populationSize: number, sampleSize: number): number {
	if (sampleSize / populationSize <= 0.05) {
		return 1; // Negligible effect
	}
	return Math.sqrt((populationSize - sampleSize) / (populationSize - 1));
}

/**
 * Adjusted margin of error with finite population correction
 */
export function adjustedMarginOfError(
	populationSize: number,
	sampleSize: number,
	proportion = 0.5,
	confidenceLevel = 0.95
): number {
	const baseMOE = marginOfError(sampleSize, proportion, confidenceLevel);
	const fpc = finitePopulationCorrection(populationSize, sampleSize);
	return baseMOE * fpc;
}

/**
 * Take a random sample from a population with a given true proportion
 * Returns the sample proportion
 */
export function takeSample(trueProportion: number, sampleSize: number): number {
	let successes = 0;
	for (let i = 0; i < sampleSize; i++) {
		if (Math.random() < trueProportion) {
			successes++;
		}
	}
	return successes / sampleSize;
}

/**
 * Take multiple samples and return the results
 */
export function takeMultipleSamples(
	trueProportion: number,
	sampleSize: number,
	numSamples: number
): number[] {
	const results: number[] = [];
	for (let i = 0; i < numSamples; i++) {
		results.push(takeSample(trueProportion, sampleSize));
	}
	return results;
}

/**
 * Calculate what percentage of samples fall within the margin of error
 */
export function samplesWithinMOE(
	samples: number[],
	trueProportion: number,
	moe: number
): number {
	const withinMOE = samples.filter(
		(sample) => Math.abs(sample - trueProportion) <= moe
	).length;
	return withinMOE / samples.length;
}

/**
 * Generate data points for the MOE curve (1/sqrt(n))
 */
export function generateMOECurveData(
	minN: number,
	maxN: number,
	steps: number,
	confidenceLevel = 0.95
): Array<{ n: number; moe: number }> {
	const data: Array<{ n: number; moe: number }> = [];
	const stepSize = (maxN - minN) / steps;

	for (let i = 0; i <= steps; i++) {
		const n = Math.round(minN + i * stepSize);
		data.push({
			n,
			moe: marginOfError(n, 0.5, confidenceLevel) * 100 // Convert to percentage
		});
	}

	return data;
}

/**
 * Calculate histogram bins from sample data
 */
export function createHistogramBins(
	samples: number[],
	numBins: number
): Array<{ binStart: number; binEnd: number; count: number; percentage: number }> {
	const min = Math.min(...samples);
	const max = Math.max(...samples);
	const binWidth = (max - min) / numBins;

	const bins: Array<{ binStart: number; binEnd: number; count: number; percentage: number }> = [];

	for (let i = 0; i < numBins; i++) {
		const binStart = min + i * binWidth;
		const binEnd = binStart + binWidth;
		const count = samples.filter((s) => s >= binStart && (i === numBins - 1 ? s <= binEnd : s < binEnd)).length;

		bins.push({
			binStart,
			binEnd,
			count,
			percentage: (count / samples.length) * 100
		});
	}

	return bins;
}

/**
 * Format a number as a percentage string
 */
export function formatPercent(value: number, decimals = 1): string {
	return `${(value * 100).toFixed(decimals)}%`;
}

/**
 * Format margin of error for display
 */
export function formatMOE(moe: number): string {
	return `±${(moe * 100).toFixed(1)}%`;
}

/**
 * Generate a normally distributed random number using Box-Muller transform
 */
export function randomNormal(mean: number, stdDev: number): number {
	const u1 = Math.random();
	const u2 = Math.random();
	const z = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
	return mean + z * stdDev;
}

/**
 * Convert inches to feet and inches string
 */
export function inchesToFeetInches(inches: number): string {
	const feet = Math.floor(inches / 12);
	const remainingInches = Math.round(inches % 12);
	return `${feet}'${remainingInches}"`;
}

/**
 * Calculate mean of an array
 */
export function mean(values: number[]): number {
	if (values.length === 0) return 0;
	return values.reduce((sum, v) => sum + v, 0) / values.length;
}

/**
 * Calculate standard deviation of an array
 */
export function standardDeviation(values: number[]): number {
	if (values.length < 2) return 0;
	const avg = mean(values);
	const squaredDiffs = values.map((v) => Math.pow(v - avg, 2));
	return Math.sqrt(squaredDiffs.reduce((sum, v) => sum + v, 0) / (values.length - 1));
}

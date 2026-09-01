import test from 'node:test';
import assert from 'node:assert/strict';
import { defaultCalculationName } from './compareResultsHelpers.js';

test('defaultCalculationName creates numbered result names', () => {
  assert.equal(defaultCalculationName(0), 'Rechnung 1');
  assert.equal(defaultCalculationName(2), 'Rechnung 3');
});

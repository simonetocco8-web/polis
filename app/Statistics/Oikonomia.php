<?php

namespace App\Statistics;

use RuntimeException;

final class Oikonomia
{
    public const METRICS = [
        'gdp', 'real_gdp', 'gdp_per_capita', 'value_added', 'gross_output_value', 'intermediate_value',
        'consumption', 'investment', 'stock_change', 'public_consumption', 'wages', 'surplus', 'productivity',
        'price_cents', 'next_price_cents', 'cpi', 'inflation_monthly_percent',
        'population', 'labor_force', 'employed', 'unemployed', 'unemployment_percent', 'firms_active',
        'desired_units', 'purchased_units', 'units_produced', 'inventory_units', 'capital_units',
        'median_person_income', 'income_gini', 'poverty_percent', 'deprived_households',
        'household_deposits', 'household_deposit_change', 'household_debt', 'firm_deposits', 'firm_debt',
        'public_debt', 'public_revenue', 'public_spending', 'fiscal_balance', 'debt_gdp_percent', 'deficit_gdp_percent',
        'cash_balance', 'bank_loans', 'bank_equity', 'bank_reserves', 'bank_deposits', 'bank_credit_losses', 'firm_failures',
    ];

    public function load(): array
    {
        $path = config('polis.content').'/statistics/oikonomia';
        $raw = file_get_contents($path.'.json');
        $expected = file_get_contents($path.'.sha256');
        $this->require($raw !== false && $expected !== false && hash_equals(trim($expected), hash('sha256', $raw)), 'Hash del file non valido');
        $data = json_decode($raw, true, flags: JSON_THROW_ON_ERROR);
        $this->validate($data);

        return $data;
    }

    public function validate(array $data): void
    {
        $keys = ['schema', 'model', 'scenario', 'status', 'demos_origin', 'config_sha256', 'initial_sha256', 'final_sha256',
            'journal_sha256', 'generated_at', 'opening_population', 'opening_households', 'opening_firms', 'months',
            'base_year', 'reference', 'trade', 'polis_index', 'rows'];
        $this->hasKeys($data, $keys);
        $demos = app(Demos::class)->load();
        $this->require($data['schema'] === 'oikonomia-aggregate-1' && $data['model'] === '0.4.0'
            && $data['scenario'] === 'baseline' && $data['status'] === 'prova-tecnica-non-calibrata'
            && $data['opening_population'] === 100000 && $data['opening_firms'] === 5000
            && $data['demos_origin'] === $demos['snapshot_sha256'] && $data['opening_households'] === $demos['totals']['households']
            && $data['reference'] === 'eu27' && $data['base_year'] === 2022
            && $data['trade'] === 'economia-chiusa' && $data['polis_index'] === null, 'Provenienza non valida');
        foreach (['demos_origin', 'config_sha256', 'initial_sha256', 'final_sha256', 'journal_sha256'] as $key) {
            $this->require(is_string($data[$key]) && preg_match('/\A[0-9a-f]{64}\z/', $data[$key]) === 1, 'Hash non valido');
        }
        $this->require(is_string($data['generated_at']) && preg_match('/\A\d{4}-\d{2}-\d{2}T[0-9:.]+\+00:00\z/', $data['generated_at']) === 1,
            'Timestamp non valido');
        $this->require(is_int($data['months']) && $data['months'] > 0 && $data['months'] <= 600
            && is_array($data['rows']) && array_is_list($data['rows']) && count($data['rows']) === $data['months'], 'Serie non valida');
        foreach ($data['rows'] as $index => $row) {
            $this->hasKeys($row, [...self::METRICS, 'month', 'gdp_expenditure', 'gdp_income', 'public_arrears', 'bank_credit_halted', 'income_by_region']);
            foreach (self::METRICS as $key) {
                $value = $row[$key];
                $this->require($value === null || ((is_float($value) || is_int($value)) && is_finite($value) && abs($value) <= 10 ** 14), 'Valore numerico non valido');
            }
            $this->require($row['month'] === $index + 1 && is_bool($row['public_arrears']) && is_bool($row['bank_credit_halted'])
                && is_array($row['income_by_region']) && count($row['income_by_region']) === 3
                && count(array_filter($row['income_by_region'], static fn ($value) => is_int($value) && $value >= 0)) === 3,
                'Periodo o redditi territoriali non validi');
            $this->require(is_int($row['gdp']) && $row['gdp'] === $row['gdp_expenditure'] && $row['gdp'] === $row['gdp_income']
                && $row['gdp'] === $row['consumption'] + $row['public_consumption'] + $row['investment'] + $row['stock_change'],
                'PIL non riconciliato');
            $this->require($row['bank_loans'] === $row['household_debt'] + $row['firm_debt'] + $row['public_debt']
                && $row['bank_reserves'] + $row['bank_loans'] === $row['bank_deposits'] + $row['bank_equity'],
                'Bilancio bancario non riconciliato');
            $this->require($row['bank_deposits'] === $row['household_deposits'] + $row['firm_deposits'] + $row['cash_balance']
                && $row['fiscal_balance'] === $row['public_revenue'] - $row['public_spending']
                && $row['labor_force'] === $row['employed'] + $row['unemployed']
                && $row['purchased_units'] <= $row['desired_units'] && $row['inventory_units'] >= 0 && $row['price_cents'] > 0,
                'Aggregati incoerenti');
        }
    }

    private function hasKeys(array $row, array $keys): void
    {
        $this->require(count($row) === count($keys) && array_diff($keys, array_keys($row)) === [], 'Campi non previsti');
    }

    private function require(bool $ok, string $message): void
    {
        if (! $ok) {
            throw new RuntimeException('Esportazione Oikonomia non valida: '.$message);
        }
    }
}

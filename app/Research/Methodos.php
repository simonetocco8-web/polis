<?php

namespace App\Research;

use Illuminate\Support\Facades\File;
use InvalidArgumentException;

final class Methodos
{
    private const MATURITY = ['hypothesized', 'calibrated', 'validated', 'frozen'];

    private const REQUIREMENTS = [
        'frozen_protocol', 'calibration_sources', 'implemented_regimes', 'equations_parameters',
        'metrics_thresholds', 'replication_power_seeds_stopping', 'stress_profiles', 'independent_validation',
        'costs_resources', 'incident_and_reporting_rules',
    ];

    public function load(): array
    {
        $config = File::json(config('polis.content').'/research/methodos-1.0.json');
        $this->validate($config);

        return $config;
    }

    public function validate(array $config): void
    {
        if (($config['version'] ?? null) !== '1.0' || ($config['protocol_version'] ?? null) !== '1.0'
            || ! in_array($config['maturity'] ?? null, self::MATURITY, true)) {
            throw new InvalidArgumentException('Versione o maturità sperimentale non valida.');
        }
        foreach (['initial_conditions', 'scenarios', 'indicators', 'polis_index', 'failure_rules', 'crisis_profiles', 'preregistration', 'sources'] as $section) {
            if (! is_array($config[$section] ?? null) || $config[$section] === []) {
                throw new InvalidArgumentException("Sezione di configurazione mancante: {$section}");
            }
        }
        $initial = $config['initial_conditions'];
        if (array_diff(['population', 'firms', 'annual_gdp_eur', 'gdp_capita_eur', 'unemployment_pct', 'inflation_pct', 'debt_gdp_pct', 'life_expectancy_years', 'years', 'monthly_steps', 'empirical_reference'], array_keys($initial))
            || $initial['population'] <= 0 || $initial['monthly_steps'] !== $initial['years'] * 12
            || $initial['annual_gdp_eur'] !== $initial['gdp_capita_eur'] * $initial['population']) {
            throw new InvalidArgumentException('Condizioni iniziali incomplete o incoerenti.');
        }
        if (array_column($config['scenarios'], 'id') !== range('A', 'F')
            || array_diff(self::REQUIREMENTS, array_keys($config['preregistration']))) {
            throw new InvalidArgumentException('Scenari o prerequisiti sperimentali incompleti.');
        }
        foreach ($config['scenarios'] as $scenario) {
            $this->requireFields($scenario, ['name', 'decision', 'limits', 'objective', 'comparison', 'status', 'reference']);
        }
        foreach (['indicators', 'failure_rules', 'crisis_profiles'] as $group) {
            $ids = array_column($config[$group], 'id');
            if (count($ids) !== count($config[$group]) || count($ids) !== count(array_unique($ids))) {
                throw new InvalidArgumentException("Identificativi assenti o duplicati: {$group}");
            }
        }
        foreach ($config['indicators'] as $indicator) {
            $this->requireFields($indicator, ['id', 'name', 'category', 'definition', 'unit', 'frequency', 'direction', 'status', 'version']);
            if (array_diff(['formula', 'source', 'threshold'], array_keys($indicator))
                || ! in_array($indicator['status'], self::MATURITY, true)
                || (isset($indicator['source']) && ! isset($config['sources'][$indicator['source']]))) {
                throw new InvalidArgumentException('Indicatore non valido.');
            }
        }
        $domains = $config['polis_index']['domains'] ?? [];
        $ids = ['prosperity', 'wellbeing', 'equity', 'freedom', 'sustainability', 'stability'];
        if (array_column($domains, 'id') !== $ids || array_column($domains, 'weight') !== [25, 25, 15, 15, 10, 10]
            || ($config['polis_index']['rights_veto'] ?? null) !== true) {
            throw new InvalidArgumentException('Composizione del Polis Index non valida.');
        }
        foreach ($domains as $domain) {
            $this->requireFields($domain, ['name']);
        }
        foreach ($config['failure_rules'] as $rule) {
            $this->requireFields($rule, ['id', 'rule']);
            $threshold = $rule['threshold'] ?? null;
            if ($threshold !== null && (! in_array($threshold['operator'] ?? null, ['>', '>='], true)
                || ! is_int($threshold['percent'] ?? null) || $threshold['percent'] < 0 || $threshold['percent'] > 100
                || ! is_int($threshold['months'] ?? null) || $threshold['months'] < 1)) {
                throw new InvalidArgumentException('Soglia di fallimento non valida.');
            }
        }
        foreach ($config['crisis_profiles'] as $profile) {
            $this->requireFields($profile, ['id', 'status']);
            if (! in_array($profile['status'], self::MATURITY, true) || ! array_key_exists('parameters', $profile)) {
                throw new InvalidArgumentException('Profilo di crisi non valido.');
            }
        }
        if ($config['maturity'] === 'frozen' && ! $this->ready($config)) {
            throw new InvalidArgumentException('Il congelamento richiede tutti i prerequisiti e le evidenze.');
        }
    }

    public function ready(array $config): bool
    {
        if (($config['maturity'] ?? null) !== 'frozen'
            || ! $this->hasEvidence($config['initial_conditions']['empirical_reference'] ?? null)
            || ! $this->hasEvidence($config['polis_index']['normalization'] ?? null)
            || ! $this->hasEvidence($config['polis_index']['missing_data'] ?? null)
            || array_column($config['scenarios'] ?? [], 'status') !== array_fill(0, 6, 'frozen')) {
            return false;
        }
        foreach (self::REQUIREMENTS as $requirement) {
            if (! $this->hasEvidence($config['preregistration'][$requirement] ?? null)) {
                return false;
            }
        }
        foreach ($config['indicators'] as $indicator) {
            if ($indicator['status'] !== 'frozen' || ! $this->hasEvidence($indicator['formula'] ?? null)) {
                return false;
            }
        }
        foreach ($config['crisis_profiles'] as $profile) {
            if ($profile['status'] !== 'frozen' || empty($profile['parameters'])) {
                return false;
            }
        }

        return true;
    }

    public function score(array $domains, array $scores, bool $seriousViolation): ?float
    {
        if ($seriousViolation || count($scores) !== count($domains)) {
            return null;
        }
        $total = 0;
        foreach ($domains as $domain) {
            $score = $scores[$domain['id']] ?? null;
            if ((! is_int($score) && ! is_float($score)) || ! is_finite($score) || $score < 0 || $score > 100) {
                return null;
            }
            $total += $score * $domain['weight'];
        }

        return $total / 100;
    }

    private function requireFields(array $row, array $fields): void
    {
        foreach ($fields as $field) {
            if (! is_string($row[$field] ?? null) || trim($row[$field]) === '') {
                throw new InvalidArgumentException("Campo mancante o non valido: {$field}");
            }
        }
    }

    private function hasEvidence(mixed $value): bool
    {
        return is_string($value) && trim($value) !== '' && mb_strtolower(trim($value)) !== 'da definire';
    }
}

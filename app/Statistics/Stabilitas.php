<?php

namespace App\Statistics;

use RuntimeException;

final class Stabilitas
{
    public const HISTORY = [
        'version' => '0.4.0',
        'opening_sha256' => 'd12de75af361ccf5fb46d1f972894b0068a6ac3f21273b710e128155a93e2313',
        'final_sha256' => 'f9aa3a372a02828eb612494f59403de2c06911b5a9e25373a980c1f0ecf2f6b2',
        'events_sha256' => '135af7b434a0472b94f92414aaa388a4bdd70f8a54814541d85c18d0057e00a5',
    ];

    public function load(): array
    {
        $path = config('polis.content').'/statistics/stabilitas';
        $raw = file_get_contents($path.'.json');
        $checksum = file_get_contents($path.'.sha256');
        $this->require($raw !== false && $checksum !== false && hash_equals(trim($checksum), hash('sha256', $raw)), 'Checksum non valido');
        $data = json_decode($raw, true, flags: JSON_THROW_ON_ERROR);
        $this->validate($data);

        return $data;
    }

    public function validate(array $data): void
    {
        $keys = ['schema', 'release', 'model', 'status', 'generated_at', 'polis_index', 'historical', 'design', 'standard', 'exploratory', 'paired_deltas'];
        $this->require(count($data) === count($keys) && array_diff($keys, array_keys($data)) === []
            && $data['schema'] === 'stabilitas-aggregate-1' && $data['release'] === '0.4.1' && $data['model'] === 'stabilitas-1'
            && $data['status'] === 'prove-tecniche-non-calibrate' && $data['polis_index'] === null
            && $data['historical'] == self::HISTORY, 'Provenienza o schema incompatibile');
        $standard = $data['standard'];
        $this->require(array_column($standard, 'experiment') === ['control', 'R', 'C', 'B+C+E', 'D']
            && count($data['exploratory']) === 30 && count($data['paired_deltas']) === 9, 'Disegno incompleto');
        $original = app(Oikonomia::class)->load();
        foreach ($standard as $index => $run) {
            $this->require($run['months'] === 600 && $run['profile'] === 'standard' && $run['seed'] === 20261122
                && $run['opening_sha256'] === self::HISTORY['opening_sha256']
                && $run['demos_sha256'] === $original['demos_origin'], 'Apertura non accoppiata');
            foreach (['final_sha256', 'initial_sha256', 'journal_sha256', 'experiment_sha256'] as $hash) {
                $this->require(is_string($run[$hash] ?? null) && preg_match('/\A[0-9a-f]{64}\z/', $run[$hash]) === 1, 'Hash non valido');
            }
            $this->require(! isset($run['enterprise_entries']) && count($run['enterprise_entries_by_sector']) === 5
                && array_sum($run['enterprise_entries_by_sector']) === $run['metrics']['total_entries'], 'Ingressi non aggregati');
            $months = $index === 0 ? range(1, 600) : [1, ...range(12, 600, 12)];
            $this->require(array_column($run['rows'], 'month') === $months, 'Orizzonte non valido');
            if ($index === 0) {
                $this->require($run['final_sha256'] === self::HISTORY['final_sha256']
                    && $run['journal_sha256'] === $original['journal_sha256'], 'Baseline divergente');
            }
            foreach ($run['rows'] as $i => $row) {
                $this->require(is_int($row['gdp'] ?? null) && $row['gdp'] === $row['journal_expenditure']
                    && $row['bank_deposits'] === $row['cash_balance'] + $row['household_deposits'] + $row['firm_deposits']
                    && $row['units_produced'] === array_sum($row['sector_output']), 'Identità aggregate non riconciliate');
                if ($index === 0) {
                    foreach (['gdp', 'employed', 'bank_deposits', 'firms_active', 'units_produced'] as $key) {
                        $this->require($row[$key] === $original['rows'][$i][$key], 'Riga storica divergente');
                    }
                }
            }
        }
    }

    private function require(bool $condition, string $message): void
    {
        if (! $condition) {
            throw new RuntimeException('Esportazione Stabilitas non valida: '.$message);
        }
    }
}

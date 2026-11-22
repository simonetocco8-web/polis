<?php

namespace App\Statistics;

use Illuminate\Support\Facades\File;
use RuntimeException;

final class Demos
{
    public const GROUPS = [
        'age' => 'persone', 'age_f' => 'persone', 'age_m' => 'persone', 'households' => 'nuclei',
        'education' => 'persone', 'employment' => 'persone', 'health' => 'persone',
        'sectors' => 'imprese', 'firm_sizes' => 'imprese', 'territories' => 'persone',
        'dwelling_capacity' => 'abitazioni',
    ];

    public function load(): array
    {
        $data = File::json(config('polis.content').'/statistics/demos.json', JSON_THROW_ON_ERROR);
        $this->validate($data);

        return $data;
    }

    public function validate(array $data): void
    {
        $metadata = ['calibration', 'config_sha256', 'definitions', 'generated_at', 'generator', 'groups', 'macro_targets',
            'month', 'polis_index', 'profile', 'reference', 'schema', 'snapshot_sha256', 'sources', 'totals'];
        $this->require(array_diff(array_keys($data), $metadata) === [] && count($data) === count($metadata), 'Campi inattesi');
        $this->require($data['schema'] === 'demos-aggregate-1' && $data['profile'] === 'standard'
            && $data['generator'] === '0.3.0' && $data['month'] === 0 && $data['reference'] === 'eu27'
            && $data['polis_index'] === null, 'Metadati non validi');
        foreach (['snapshot_sha256', 'config_sha256'] as $key) {
            $this->require(is_string($data[$key]) && preg_match('/\A[0-9a-f]{64}\z/', $data[$key]) === 1, 'Hash non valido');
        }
        $this->require(is_string($data['generated_at']) && preg_match('/\A\d{4}-\d{2}-\d{2}T[0-9:.]+\+00:00\z/', $data['generated_at']) === 1
            && $data['calibration'] === 'parziale: età/sesso iniziali e mortalità UE-27 2022', 'Provenienza non valida');
        $this->require(is_array($data['groups']) && count($data['groups']) === count(self::GROUPS), 'Gruppi non validi');
        foreach (array_keys(self::GROUPS) as $key) {
            $group = $data['groups'][$key] ?? null;
            $this->require(is_array($group) && count($group) > 0 && count($group) <= 25, 'Gruppo non valido');
            foreach ($group as $label => $count) {
                $this->require(is_string($label) && mb_strlen($label) <= 80 && is_int($count) && $count >= 0, 'Valore aggregato non valido');
            }
        }

        $totals = $data['totals'];
        $this->require(is_array($totals) && count($totals) === 7 && ($totals['population'] ?? null) === 100000
            && ($totals['firms'] ?? null) === 5000, 'Totali non validi');
        foreach (['households', 'labor_force', 'unemployed'] as $key) {
            $this->require(is_int($totals[$key] ?? null) && $totals[$key] >= 0 && $totals[$key] <= $totals['population'], 'Conteggio non valido');
        }
        $groups = $data['groups'];
        foreach (['age', 'education', 'employment', 'health', 'territories'] as $key) {
            $this->require(array_sum($groups[$key]) === $totals['population'], 'Distribuzione non riconciliata');
        }
        foreach (['sectors', 'firm_sizes'] as $key) {
            $this->require(array_sum($groups[$key]) === $totals['firms'], 'Imprese non riconciliate');
        }
        $this->require(array_sum($groups['households']) === $totals['households'], 'Famiglie non riconciliate');
        foreach ($groups['age'] as $band => $count) {
            $this->require(isset($groups['age_f'][$band], $groups['age_m'][$band])
                && $groups['age_f'][$band] + $groups['age_m'][$band] === $count, 'Piramide non riconciliata');
        }
        $this->require(count($groups['age']) === count($groups['age_f']) && count($groups['age']) === count($groups['age_m']), 'Fasce incoerenti');
        $this->require(($groups['employment']['Disoccupati'] ?? null) === $totals['unemployed']
            && isset($groups['employment']['Fuori forza lavoro'])
            && $totals['labor_force'] === $totals['population'] - $groups['employment']['Fuori forza lavoro']
            && $totals['labor_force'] > 0
            && ($totals['unemployment_percent'] ?? null) == round(100 * $totals['unemployed'] / $totals['labor_force'], 2)
            && is_numeric($totals['mean_age_years'] ?? null) && $totals['mean_age_years'] >= 0, 'Forza lavoro incoerente');
        $this->require(is_array($data['sources']) && array_column($data['sources'], 'code') === ['demo_mlifetable', 'demo_pjan'], 'Fonti non valide');
        foreach ($data['sources'] as $source) {
            $this->require(isset($source['agency'], $source['period'], $source['url'], $source['sha256'])
                && is_string($source['url']) && str_starts_with($source['url'], 'https://ec.europa.eu/eurostat/'), 'Fonte non valida');
        }
        $this->require(is_array($data['macro_targets']) && is_array($data['definitions']), 'Definizioni non valide');
        foreach ($data['macro_targets'] as $value) {
            $this->require((is_int($value) || is_float($value)) && is_finite($value), 'Ipotesi macro non valida');
        }
    }

    private function require(bool $condition, string $message): void
    {
        if (! $condition) {
            throw new RuntimeException('Esportazione Demos non valida: '.$message);
        }
    }
}

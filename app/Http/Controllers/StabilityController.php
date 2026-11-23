<?php

namespace App\Http\Controllers;

use App\Statistics\Stabilitas;
use Illuminate\Contracts\View\View;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\StreamedResponse;

final class StabilityController
{
    public function show(Stabilitas $audit): View
    {
        $data = $audit->load();
        $baseline = $data['standard'][0];
        $series = [
            'employed' => 'Occupati', 'units_produced' => 'Produzione fisica', 'firm_deposits' => 'Depositi delle imprese',
            'cash_balance' => 'Cassa del Tesoro',
        ];
        $charts = [];
        foreach ($series as $key => $label) {
            $values = array_column($baseline['rows'], $key);
            $low = min($values);
            $high = max($values);
            $points = [];
            foreach ($values as $i => $value) {
                $points[] = sprintf('%.2F,%.2F', 10 + 580 * $i / 599, 135 - 115 * ($value - $low) / max(1, $high - $low));
            }
            $documentedUnits = in_array($key, ['firm_deposits', 'cash_balance'], true) ? 'centesimi' : 'unità';
            $charts[] = ['label' => $label, 'low' => $low, 'high' => $high, 'unit' => $documentedUnits, 'points' => implode(' ', $points)];
        }

        return view('stability', ['title' => 'Stabilità economica', 'data' => $data, 'baseline' => $baseline, 'charts' => $charts]);
    }

    public function download(Stabilitas $audit, string $format): Response
    {
        $data = $audit->load();
        if ($format === 'json') {
            return response()->file(config('polis.content').'/statistics/stabilitas.json', [
                'Content-Type' => 'application/json', 'Content-Disposition' => 'attachment; filename="nova-stabilitas.json"',
            ]);
        }

        return new StreamedResponse(static function () use ($data): void {
            $fields = ['month', 'gdp', 'employed', 'units_produced', 'capital_units', 'inventory_units', 'desired_units',
                'household_deposits', 'firm_deposits', 'cash_balance', 'public_debt', 'transfers_due', 'transfers_paid',
                'bank_equity', 'bank_distribution', 'real_median_income', 'cpi', 'entries', 'firm_failures'];
            $out = fopen('php://output', 'w');
            fputcsv($out, ['experiment', ...$fields, 'loan_origination', 'principal_repaid', 'interest_received'], escape: '');
            foreach ($data['standard'] as $run) {
                foreach ($run['rows'] as $row) {
                    fputcsv($out, [$run['experiment'], ...array_map(static fn ($key) => $row[$key], $fields),
                        array_sum($row['origination']), array_sum($row['principal']), array_sum($row['interest'])], escape: '');
                }
            }
            fclose($out);
        }, 200, ['Content-Type' => 'text/csv; charset=UTF-8', 'Content-Disposition' => 'attachment; filename="nova-stabilitas.csv"']);
    }
}

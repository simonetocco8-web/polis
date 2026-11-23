<?php

namespace App\Http\Controllers;

use App\Statistics\Oikonomia;
use Illuminate\Contracts\View\View;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\StreamedResponse;

final class EconomyController
{
    public const PAGES = [
        'sintesi' => ['Economia', ['gdp', 'employed', 'cpi', 'fiscal_balance']],
        'pil' => ['PIL e contabilità nazionale', ['gdp', 'real_gdp', 'gdp_per_capita', 'value_added', 'intermediate_value', 'consumption', 'investment', 'stock_change', 'productivity']],
        'lavoro' => ['Lavoro', ['labor_force', 'employed', 'unemployed', 'unemployment_percent', 'wages']],
        'imprese' => ['Imprese', ['firms_active', 'units_produced', 'capital_units', 'inventory_units', 'surplus', 'firm_failures']],
        'prezzi' => ['Prezzi', ['price_cents', 'cpi', 'inflation_monthly_percent']],
        'famiglie' => ['Famiglie', ['desired_units', 'purchased_units', 'deprived_households', 'median_person_income', 'consumption']],
        'ricchezza' => ['Redditi e patrimoni finanziari', ['median_person_income', 'income_gini', 'poverty_percent', 'household_deposits', 'household_debt']],
        'banche' => ['Banca e credito', ['bank_deposits', 'bank_loans', 'bank_equity', 'bank_reserves', 'bank_credit_losses']],
        'finanza-pubblica' => ['Finanza pubblica', ['public_revenue', 'public_spending', 'fiscal_balance', 'public_debt', 'debt_gdp_percent', 'deficit_gdp_percent']],
        'commercio' => ['Commercio con l’estero', []],
        'metodologia' => ['Metodologia economica', []],
    ];

    private const LABELS = [
        'gdp' => ['PIL nominale mensile', 'EUR'], 'real_gdp' => ['PIL reale mensile (base 2022)', 'EUR'],
        'gdp_per_capita' => ['PIL mensile per residente', 'EUR'], 'value_added' => ['Valore aggiunto lordo', 'EUR'],
        'intermediate_value' => ['Consumi intermedi', 'EUR'], 'consumption' => ['Consumi delle famiglie', 'EUR'],
        'investment' => ['Investimenti fissi', 'EUR'], 'stock_change' => ['Variazione delle scorte', 'EUR'],
        'productivity' => ['Valore aggiunto privato per addetto', 'EUR'], 'employed' => ['Occupati', 'persone'],
        'unemployed' => ['Disoccupati', 'persone'], 'labor_force' => ['Forza lavoro', 'persone'],
        'unemployment_percent' => ['Tasso di disoccupazione', '%'], 'wages' => ['Retribuzioni', 'EUR'],
        'firms_active' => ['Imprese attive', 'imprese'], 'units_produced' => ['Unità prodotte', 'unità'],
        'capital_units' => ['Capitale produttivo', 'unità'], 'inventory_units' => ['Scorte', 'unità'],
        'surplus' => ['Risultato operativo lordo aggregato', 'EUR'], 'firm_failures' => ['Cessazioni nel mese', 'imprese'],
        'price_cents' => ['Prezzo del bene composito al netto dell’imposta', 'EUR'], 'cpi' => ['Indice dei prezzi al consumo (2022 = 100)', 'indice'],
        'inflation_monthly_percent' => ['Inflazione mensile', '%'], 'desired_units' => ['Unità desiderate dalle famiglie', 'unità'],
        'purchased_units' => ['Unità acquistate dalle famiglie', 'unità'], 'deprived_households' => ['Nuclei sotto il fabbisogno essenziale ipotizzato', 'nuclei'],
        'median_person_income' => ['Reddito disponibile mediano per membro del nucleo', 'EUR'],
        'income_gini' => ['Gini del reddito pro capite tra nuclei', 'indice'], 'poverty_percent' => ['Nuclei sotto il 60% della mediana', '%'],
        'household_deposits' => ['Depositi delle famiglie', 'EUR'], 'household_debt' => ['Debito delle famiglie', 'EUR'],
        'bank_deposits' => ['Passività per depositi', 'EUR'], 'bank_loans' => ['Crediti bancari', 'EUR'],
        'bank_equity' => ['Patrimonio netto bancario', 'EUR'], 'bank_reserves' => ['Riserve bancarie', 'EUR'],
        'bank_credit_losses' => ['Perdite su crediti nel mese', 'EUR'], 'public_revenue' => ['Entrate pubbliche', 'EUR'],
        'public_spending' => ['Uscite pubbliche', 'EUR'], 'fiscal_balance' => ['Saldo pubblico', 'EUR'],
        'public_debt' => ['Debito pubblico', 'EUR'], 'debt_gdp_percent' => ['Debito / PIL mobile annuo', '%'],
        'deficit_gdp_percent' => ['Deficit / PIL mobile annuo', '%'],
    ];

    public function show(Oikonomia $economy, string $section = 'sintesi'): View
    {
        abort_unless(isset(self::PAGES[$section]), 404);
        [$title, $fields] = self::PAGES[$section];
        $data = $economy->load();
        $last = $data['rows'][count($data['rows']) - 1];
        $metric = $fields[0] ?? null;
        $chart = $metric === null ? [] : $this->chart($data['rows'], $metric);

        return view('economy', ['title' => $title, 'section' => $section, 'data' => $data, 'last' => $last,
            'pages' => self::PAGES, 'fields' => $fields, 'labels' => self::LABELS, 'chart' => $chart,
            'format' => static fn ($value, $unit): string => $value === null ? 'Non disponibile' :
                number_format($unit === 'EUR' ? $value / 100 : $value, in_array($unit, ['EUR', '%', 'indice']) ? 2 : 0, ',', '.')]);
    }

    public function download(Oikonomia $economy, string $format): Response
    {
        $data = $economy->load();
        if ($format === 'json') {
            return response()->file(config('polis.content').'/statistics/oikonomia.json', [
                'Content-Type' => 'application/json', 'Content-Disposition' => 'attachment; filename="nova-oikonomia.json"',
            ]);
        }

        return new StreamedResponse(static function () use ($data): void {
            $stream = fopen('php://output', 'w');
            fputcsv($stream, ['month', ...Oikonomia::METRICS], escape: '');
            foreach ($data['rows'] as $row) {
                fputcsv($stream, [$row['month'], ...array_map(static fn ($key) => $row[$key], Oikonomia::METRICS)], escape: '');
            }
            fclose($stream);
        }, 200, ['Content-Type' => 'text/csv; charset=UTF-8', 'Content-Disposition' => 'attachment; filename="nova-oikonomia.csv"']);
    }

    private function chart(array $rows, string $metric): array
    {
        $values = array_column($rows, $metric);
        $numeric = array_filter($values, static fn ($value) => $value !== null);
        if ($numeric === []) {
            return [];
        }
        $low = min($numeric);
        $high = max($numeric);
        $points = [];
        foreach ($numeric as $i => $value) {
            $x = 10 + 580 * $i / max(1, count($rows) - 1);
            $y = 135 - 115 * ($value - $low) / max(1, $high - $low);
            $points[] = sprintf('%.2F,%.2F', $x, $y);
        }

        return ['points' => implode(' ', $points), 'low' => $low, 'high' => $high, 'last' => end($numeric)];
    }
}
